import uuid
import datetime
import hashlib
from typing import List, Dict, Any, Tuple
from neo4j import AsyncGraphDatabase
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.config.settings import get_settings
from backend.database.models import Criminal, FIR, Vehicle, PhoneNumber, KnownLocation, CriminalFIR

settings = get_settings()

class Neo4jService:
    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        return self._driver

    async def close(self) -> None:
        if getattr(self, "_driver", None) is not None:
            try:
                await self._driver.close()
            except Exception:
                pass
            finally:
                self._driver = None

    def _get_deterministic_uuid(self, value: str) -> str:
        """Helper to generate a consistent UUID from a string value (phone, license plate, location name)"""
        return str(uuid.UUID(bytes=hashlib.md5(value.encode('utf-8')).digest()))

    async def upsert_criminal(self, criminal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a Criminal node in Neo4j"""
        query = """
        MERGE (c:Criminal {id: $id})
        SET c.name = $name,
            c.risk_score = $risk_score,
            c.aliases = $aliases,
            c.status = $status
        RETURN c
        """
        async with self.driver.session() as session:
            result = await session.run(
                query,
                id=str(criminal_data["id"]),
                name=criminal_data["name"],
                risk_score=float(criminal_data.get("risk_score", 0.0)),
                aliases=list(criminal_data.get("aliases", [])),
                status=criminal_data["status"]
            )
            record = await result.single()
            return dict(record["c"]) if record else {}

    async def upsert_fir(self, fir_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update an FIR node in Neo4j"""
        query = """
        MERGE (f:FIR {id: $id})
        SET f.fir_number = $fir_number,
            f.crime_type = $crime_type,
            f.date_filed = $date_filed,
            f.location_name = $location_name,
            f.district = $district
        RETURN f
        """
        # Convert date_filed to ISO string if it is datetime
        date_filed_str = fir_data["date_filed"]
        if isinstance(date_filed_str, (datetime.datetime, datetime.date)):
            date_filed_str = date_filed_str.isoformat()

        async with self.driver.session() as session:
            result = await session.run(
                query,
                id=str(fir_data["id"]),
                fir_number=fir_data["fir_number"],
                crime_type=fir_data["crime_type"],
                date_filed=date_filed_str,
                location_name=fir_data.get("location_name"),
                district=fir_data.get("district")
            )
            record = await result.single()
            return dict(record["f"]) if record else {}

    async def create_relationship(
        self,
        from_id: str,
        from_label: str,
        to_id: str,
        to_label: str,
        rel_type: str,
        properties: Dict[str, Any] = None
    ) -> None:
        """Generic method to create a relationship between two nodes"""
        # Sanitize labels and relationship types to prevent Cypher injection
        if not (from_label.isalnum() and to_label.isalnum() and rel_type.replace("_", "").isalnum()):
            raise ValueError("Labels and relationship types must be strictly alphanumeric/underscores.")

        query = f"""
        MERGE (from:{from_label} {{id: $from_id}})
        MERGE (to:{to_label} {{id: $to_id}})
        MERGE (from)-[r:{rel_type}]->(to)
        SET r += $properties
        RETURN r
        """
        properties = properties or {}
        # Convert dates inside properties
        cleaned_props = {}
        for k, v in properties.items():
            if isinstance(v, (datetime.date, datetime.datetime)):
                cleaned_props[k] = v.isoformat()
            else:
                cleaned_props[k] = v

        async with self.driver.session() as session:
            await session.run(
                query,
                from_id=str(from_id),
                to_id=str(to_id),
                properties=cleaned_props
            )

    async def get_criminal_network(self, criminal_id: str, depth: int = 2) -> Dict[str, Any]:
        """Fetch ego graph for a criminal up to a specified depth (1-3)"""
        depth = min(max(int(depth), 1), 3)
        query = f"""
        MATCH (c:Criminal {{id: $criminal_id}})
        OPTIONAL MATCH path = (c)-[:INVOLVED_IN|KNOWS|OWNS|USES|FREQUENTS|OCCURRED_AT|SEEN_AT|CONTACTED*{depth}]-(n)
        RETURN c, path
        """
        async with self.driver.session() as session:
            result = await session.run(query, criminal_id=str(criminal_id))
            nodes_map = {}
            edges_list = []
            seen_edges = set()

            # Helper to parse and store node
            def add_node(n):
                n_id = n.get("id")
                if not n_id or n_id in nodes_map:
                    return
                labels = list(n.labels)
                node_type = labels[0] if labels else "Unknown"
                
                # Determine user-friendly visual label
                label = (
                    n.get("name") or 
                    n.get("fir_number") or 
                    n.get("registration_number") or 
                    n.get("number") or 
                    str(n_id)
                )
                
                nodes_map[n_id] = {
                    "id": n_id,
                    "label": label,
                    "type": node_type,
                    "properties": dict(n),
                    "data": dict(n)
                }

            async for record in result:
                central_node = record["c"]
                add_node(central_node)
                
                path = record["path"]
                if path:
                    for node in path.nodes:
                        add_node(node)
                    for rel in path.relationships:
                        start_id = rel.start_node.get("id")
                        end_id = rel.end_node.get("id")
                        if not start_id or not end_id:
                            continue
                        
                        edge_key = (start_id, end_id, rel.type)
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            
                            # Get weight metric if available
                            weight = (
                                rel.get("strength") or 
                                rel.get("frequency") or 
                                rel.get("frequency_score") or 
                                1.0
                            )
                            
                            edges_list.append({
                                "source": start_id,
                                "target": end_id,
                                "type": rel.type,
                                "weight": float(weight),
                                "properties": dict(rel)
                            })

            return {
                "nodes": list(nodes_map.values()),
                "edges": edges_list
            }

    async def discover_hidden_connections(self, criminal_ids: List[str], depth: int = 2) -> Dict[str, Any]:
        """Find paths connecting any of the criminals in the list"""
        depth = min(max(int(depth), 1), 3)
        str_ids = [str(cid) for cid in criminal_ids]
        
        query = f"""
        MATCH (c1:Criminal), (c2:Criminal)
        WHERE c1.id IN $criminal_ids AND c2.id IN $criminal_ids AND c1.id < c2.id
        MATCH path = (c1)-[:INVOLVED_IN|KNOWS|OWNS|USES|FREQUENTS|OCCURRED_AT|SEEN_AT|CONTACTED*{depth}]-(c2)
        RETURN path
        """
        async with self.driver.session() as session:
            result = await session.run(query, criminal_ids=str_ids)
            nodes_map = {}
            edges_list = []
            seen_edges = set()

            def add_node(n):
                n_id = n.get("id")
                if not n_id or n_id in nodes_map:
                    return
                labels = list(n.labels)
                node_type = labels[0] if labels else "Unknown"
                label = (
                    n.get("name") or 
                    n.get("fir_number") or 
                    n.get("registration_number") or 
                    n.get("number") or 
                    str(n_id)
                )
                nodes_map[n_id] = {
                    "id": n_id,
                    "label": label,
                    "type": node_type,
                    "properties": dict(n),
                    "data": dict(n)
                }

            # Pre-add all searched criminals to ensure they appear in the visual even if disconnected
            for cid in str_ids:
                crim_q = "MATCH (c:Criminal {id: $id}) RETURN c"
                crim_res = await session.run(crim_q, id=cid)
                crim_rec = await crim_res.single()
                if crim_rec:
                    add_node(crim_rec["c"])

            async for record in result:
                path = record["path"]
                if path:
                    for node in path.nodes:
                        add_node(node)
                    for rel in path.relationships:
                        start_id = rel.start_node.get("id")
                        end_id = rel.end_node.get("id")
                        if not start_id or not end_id:
                            continue
                        
                        edge_key = (start_id, end_id, rel.type)
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            weight = (
                                rel.get("strength") or 
                                rel.get("frequency") or 
                                rel.get("frequency_score") or 
                                1.0
                            )
                            edges_list.append({
                                "source": start_id,
                                "target": end_id,
                                "type": rel.type,
                                "weight": float(weight),
                                "properties": dict(rel)
                            })

            return {
                "nodes": list(nodes_map.values()),
                "edges": edges_list
            }

    async def get_shortest_path(self, criminal_id_1: str, criminal_id_2: str) -> Dict[str, Any]:
        """Find the shortest connection path between two criminals"""
        query = """
        MATCH (c1:Criminal {id: $id1}), (c2:Criminal {id: $id2})
        MATCH path = shortestPath((c1)-[:INVOLVED_IN|KNOWS|OWNS|USES|FREQUENTS|OCCURRED_AT|SEEN_AT|CONTACTED*1..6]-(c2))
        RETURN path
        """
        async with self.driver.session() as session:
            result = await session.run(query, id1=str(criminal_id_1), id2=str(criminal_id_2))
            record = await result.single()
            if not record or not record["path"]:
                return {"nodes": [], "edges": []}

            path = record["path"]
            nodes_map = {}
            edges_list = []

            for node in path.nodes:
                n_id = node.get("id")
                labels = list(node.labels)
                node_type = labels[0] if labels else "Unknown"
                label = (
                    node.get("name") or 
                    node.get("fir_number") or 
                    node.get("registration_number") or 
                    node.get("number") or 
                    str(n_id)
                )
                nodes_map[n_id] = {
                    "id": n_id,
                    "label": label,
                    "type": node_type,
                    "properties": dict(node),
                    "data": dict(node)
                }

            for rel in path.relationships:
                weight = (
                    rel.get("strength") or 
                    rel.get("frequency") or 
                    rel.get("frequency_score") or 
                    1.0
                )
                edges_list.append({
                    "source": rel.start_node.get("id"),
                    "target": rel.end_node.get("id"),
                    "type": rel.type,
                    "weight": float(weight),
                    "properties": dict(rel)
                })

            return {
                "nodes": list(nodes_map.values()),
                "edges": edges_list
            }

    async def get_shared_links(self, criminal_ids: List[str]) -> Dict[str, Any]:
        """Find shared phone numbers, vehicles, and locations between given criminals"""
        str_ids = [str(cid) for cid in criminal_ids]
        
        # 1. Shared Phones
        phone_query = """
        MATCH (c:Criminal)-[:USES]->(p:PhoneNumber)
        WHERE c.id IN $criminal_ids
        WITH p, collect(c) AS criminals WHERE size(criminals) > 1
        RETURN p.number AS value, [crim IN criminals | {id: crim.id, name: crim.name}] AS linked_criminals
        """
        
        # 2. Shared Vehicles
        vehicle_query = """
        MATCH (c:Criminal)-[:OWNS]->(v:Vehicle)
        WHERE c.id IN $criminal_ids
        WITH v, collect(c) AS criminals WHERE size(criminals) > 1
        RETURN v.registration_number AS value, [crim IN criminals | {id: crim.id, name: crim.name}] AS linked_criminals
        """

        # 3. Shared Locations
        location_query = """
        MATCH (c:Criminal)-[:FREQUENTS]->(l:Location)
        WHERE c.id IN $criminal_ids
        WITH l, collect(c) AS criminals WHERE size(criminals) > 1
        RETURN l.name AS value, [crim IN criminals | {id: crim.id, name: crim.name}] AS linked_criminals
        """

        async with self.driver.session() as session:
            phones_res = await session.run(phone_query, criminal_ids=str_ids)
            vehicles_res = await session.run(vehicle_query, criminal_ids=str_ids)
            locations_res = await session.run(location_query, criminal_ids=str_ids)

            shared_phones = []
            async for record in phones_res:
                shared_phones.append({
                    "phone": record["value"],
                    "criminals": record["linked_criminals"]
                })

            shared_vehicles = []
            async for record in vehicles_res:
                shared_vehicles.append({
                    "registration_number": record["value"],
                    "criminals": record["linked_criminals"]
                })

            shared_locations = []
            async for record in locations_res:
                shared_locations.append({
                    "location": record["value"],
                    "criminals": record["linked_criminals"]
                })

            return {
                "phone_numbers": shared_phones,
                "vehicles": shared_vehicles,
                "locations": shared_locations
            }

    async def detect_gang_clusters(self) -> List[Dict[str, Any]]:
        """Detect criminal gang clusters using Python Connected Components over relationship graph"""
        # Retrieve all connections between criminals (knows, shared cases, phones, or vehicles)
        query = """
        MATCH (c1:Criminal)-[:KNOWS]-(c2:Criminal)
        WHERE c1.id < c2.id
        RETURN c1.id AS id1, c1.name AS name1, c2.id AS id2, c2.name AS name2, 'KNOWS' AS connection_type

        UNION

        MATCH (c1:Criminal)-[:INVOLVED_IN]->(f:FIR)<-[:INVOLVED_IN]-(c2:Criminal)
        WHERE c1.id < c2.id
        RETURN c1.id AS id1, c1.name AS name1, c2.id AS id2, c2.name AS name2, 'SHARED_FIR' AS connection_type

        UNION

        MATCH (c1:Criminal)-[:USES]->(p:PhoneNumber)<-[:USES]-(c2:Criminal)
        WHERE c1.id < c2.id
        RETURN c1.id AS id1, c1.name AS name1, c2.id AS id2, c2.name AS name2, 'SHARED_PHONE' AS connection_type

        UNION

        MATCH (c1:Criminal)-[:OWNS]->(v:Vehicle)<-[:OWNS]-(c2:Criminal)
        WHERE c1.id < c2.id
        RETURN c1.id AS id1, c1.name AS name1, c2.id AS id2, c2.name AS name2, 'SHARED_VEHICLE' AS connection_type
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            
            adj = {}
            criminals_by_id = {}

            async for record in result:
                id1 = record["id1"]
                id2 = record["id2"]
                criminals_by_id[id1] = record["name1"]
                criminals_by_id[id2] = record["name2"]

                if id1 not in adj:
                    adj[id1] = set()
                if id2 not in adj:
                    adj[id2] = set()

                adj[id1].add(id2)
                adj[id2].add(id1)

            # DFS to identify connected components
            visited = set()
            components = []

            for cid in list(criminals_by_id.keys()):
                if cid not in visited:
                    comp = []
                    stack = [cid]
                    while stack:
                        curr = stack.pop()
                        if curr not in visited:
                            visited.add(curr)
                            comp.append(curr)
                            if curr in adj:
                                stack.extend(adj[curr] - visited)
                    # A cluster needs at least 2 connected individuals
                    if len(comp) >= 2:
                        components.append(comp)

            # Format the output clusters
            gang_clusters = []
            for i, comp in enumerate(components, 1):
                members = [{"id": mid, "name": criminals_by_id[mid]} for mid in comp]
                
                # Query dominant crime type for the members of this cluster
                crime_q = """
                MATCH (c:Criminal)-[:INVOLVED_IN]->(f:FIR)
                WHERE c.id IN $member_ids
                RETURN f.crime_type AS crime_type, count(f) AS count
                ORDER BY count DESC LIMIT 1
                """
                crime_res = await session.run(crime_q, member_ids=comp)
                crime_rec = await crime_res.single()
                dominant_crime = crime_rec["crime_type"] if crime_rec else "other"

                gang_clusters.append({
                    "cluster_id": f"gang_{i:02d}",
                    "members": members,
                    "size": len(members),
                    "dominant_crime_type": dominant_crime
                })

            return gang_clusters

    async def sync_from_postgres(self, db_session) -> Dict[str, int]:
        """Fetch all data from PostgreSQL and synchronize it into Neo4j"""
        # 1. Fetch from Postgres
        criminals_res = await db_session.execute(select(Criminal))
        criminals = criminals_res.scalars().all()

        firs_res = await db_session.execute(select(FIR))
        firs = firs_res.scalars().all()

        vehicles_res = await db_session.execute(
            select(Vehicle).options(selectinload(Vehicle.owner))
        )
        vehicles = vehicles_res.scalars().all()

        phones_res = await db_session.execute(select(PhoneNumber))
        phone_numbers = phones_res.scalars().all()

        locations_res = await db_session.execute(select(KnownLocation))
        known_locations = locations_res.scalars().all()

        links_res = await db_session.execute(select(CriminalFIR))
        links = links_res.scalars().all()

        # Clear existing graph to avoid inconsistencies
        async with self.driver.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")

        counters = {"criminals": 0, "firs": 0, "locations": 0, "vehicles": 0, "phones": 0, "relationships": 0}

        # 2. Push Criminals
        for c in criminals:
            await self.upsert_criminal({
                "id": c.id,
                "name": c.name,
                "risk_score": c.risk_score,
                "aliases": c.aliases,
                "status": c.status.value
            })
            counters["criminals"] += 1

        # 3. Push FIRs and map their location name to a Location node
        for f in firs:
            await self.upsert_fir({
                "id": f.id,
                "fir_number": f.fir_number,
                "crime_type": f.crime_type.value,
                "date_filed": f.date_filed,
                "location_name": f.location_name,
                "district": f.district
            })
            counters["firs"] += 1

            if f.location_name:
                loc_id = self._get_deterministic_uuid(f.location_name)
                # Create Location node
                await self.create_relationship(
                    from_id=str(loc_id),
                    from_label="Location",
                    to_id=str(loc_id),
                    to_label="Location",
                    rel_type="OCCURRED_AT", # will just merge location node itself
                    properties={}
                )
                # Set Location properties
                set_loc_query = """
                MERGE (l:Location {id: $id})
                SET l.name = $name,
                    l.lat = $lat,
                    l.lng = $lng,
                    l.district = $district
                """
                async with self.driver.session() as session:
                    await session.run(
                        set_loc_query,
                        id=loc_id,
                        name=f.location_name,
                        lat=float(f.location_lat or 0.0),
                        lng=float(f.location_lng or 0.0),
                        district=f.district or ""
                    )
                
                # Link FIR to Location
                await self.create_relationship(
                    from_id=str(f.id),
                    from_label="FIR",
                    to_id=loc_id,
                    to_label="Location",
                    rel_type="OCCURRED_AT"
                )
                counters["locations"] += 1
                counters["relationships"] += 1

        # 4. Push Vehicles
        for v in vehicles:
            v_id = self._get_deterministic_uuid(v.registration_number)
            set_veh_query = """
            MERGE (veh:Vehicle {id: $id})
            SET veh.registration_number = $registration_number,
                veh.make = $make,
                veh.model = $model,
                veh.color = $color
            """
            async with self.driver.session() as session:
                await session.run(
                    set_veh_query,
                    id=v_id,
                    registration_number=v.registration_number,
                    make=v.make or "",
                    model=v.model or "",
                    color=v.color or ""
                )
            counters["vehicles"] += 1

            if v.owner_criminal_id:
                await self.create_relationship(
                    from_id=str(v.owner_criminal_id),
                    from_label="Criminal",
                    to_id=v_id,
                    to_label="Vehicle",
                    rel_type="OWNS"
                )
                counters["relationships"] += 1

        # 5. Push PhoneNumbers
        for p in phones_res.scalars().all(): # Re-query or list
            pass
        # Reuse local list
        for p in phone_numbers:
            p_id = self._get_deterministic_uuid(p.number)
            set_ph_query = """
            MERGE (ph:PhoneNumber {id: $id})
            SET ph.number = $number
            """
            async with self.driver.session() as session:
                await session.run(set_ph_query, id=p_id, number=p.number)
            counters["phones"] += 1

            await self.create_relationship(
                from_id=str(p.criminal_id),
                from_label="Criminal",
                to_id=p_id,
                to_label="PhoneNumber",
                rel_type="USES"
            )
            counters["relationships"] += 1

        # 6. Push KnownLocations (Frequented by suspects)
        for kl in known_locations:
            loc_id = self._get_deterministic_uuid(kl.location_name)
            set_loc_query = """
            MERGE (l:Location {id: $id})
            SET l.name = $name,
                l.lat = $lat,
                l.lng = $lng
            """
            async with self.driver.session() as session:
                await session.run(
                    set_loc_query,
                    id=loc_id,
                    name=kl.location_name,
                    lat=float(kl.lat),
                    lng=float(kl.lng)
                )

            await self.create_relationship(
                from_id=str(kl.criminal_id),
                from_label="Criminal",
                to_id=loc_id,
                to_label="Location",
                rel_type="FREQUENTS",
                properties={"frequency_score": kl.frequency_score}
            )
            counters["relationships"] += 1

        # 7. Push Suspect-FIR Links
        for link in links:
            await self.create_relationship(
                from_id=str(link.criminal_id),
                from_label="Criminal",
                to_id=str(link.fir_id),
                to_label="FIR",
                rel_type="INVOLVED_IN",
                properties={"role": link.role_in_crime}
            )
            counters["relationships"] += 1

        # 8. Create KNOWS relationships between criminals who share phone numbers or vehicles
        # (This is standard graph generation to make direct criminal links)
        knows_queries = [
            # Link criminals sharing a phone
            """
            MATCH (c1:Criminal)-[:USES]->(p:PhoneNumber)<-[:USES]-(c2:Criminal)
            WHERE c1.id < c2.id
            MERGE (c1)-[r:KNOWS]->(c2)
            SET r.strength = coalesce(r.strength, 0.0) + 0.8,
                r.last_seen = date()
            """,
            # Link criminals sharing a vehicle
            """
            MATCH (c1:Criminal)-[:OWNS|USES|SEEN_AT*1..2]-(v:Vehicle)-[:OWNS|USES|SEEN_AT*1..2]-(c2:Criminal)
            WHERE c1.id < c2.id
            MERGE (c1)-[r:KNOWS]->(c2)
            SET r.strength = coalesce(r.strength, 0.0) + 0.6,
                r.last_seen = date()
            """,
            # Link criminals involved in the same case (FIR)
            """
            MATCH (c1:Criminal)-[:INVOLVED_IN]->(f:FIR)<-[:INVOLVED_IN]-(c2:Criminal)
            WHERE c1.id < c2.id
            MERGE (c1)-[r:KNOWS]->(c2)
            SET r.strength = coalesce(r.strength, 0.0) + 0.9,
                r.last_seen = date(left(f.date_filed, 10))
            """

        ]
        async with self.driver.session() as session:
            for kq in knows_queries:
                await session.run(kq)

        return counters

neo4j_service = Neo4jService()


async def close_neo4j_driver() -> None:
    """Close the Neo4j driver connection pool."""
    await neo4j_service.close()


__all__ = ["Neo4jService", "neo4j_service", "close_neo4j_driver"]



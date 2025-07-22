This file describes some of the design choices for the data sources app, both current and historical.

# In Process Migrations

This describes migrations in design choices that are currently in process. Due to the size of the application, comprehensive migrations are not practical, so designs are migrated gradually, noting both the prior design and the new design.

## Type-Prioritized Directories to Domain-Prioritized Directories.

The prior design pattern privileged organizing files in directories by type: for example, `middleware` contains directories such as `primary_resource_logic` and `schema_and_dto`, which each contain second-level directories and files organized by domain, such as `primary_resource_logic/data_requests`, `primary_resource_logic/data_sources.py`, and so on.

Now, directory organization privileges organizing files according to their domain, starting from the `endpoints/instantiations` directory. Now, instead of a schema file being located among other schema files in `middleware/schema_and_dto/schemas` and a dto file being located in `middleware/schema_and_dto/dto`, the files would be located in `endpoints/instantiations/{endpoint_namespace}/{route}/dto` and `../schema`, respectively. 

This is done to keep files organized by domain rather than by type, and to privilege keeping files used together located as close together as possible, minimizing time spent searching the directory for related files. 

Where a file or function is shared by multiple endpoints, the file or function is moved to the `shared` that is the closest superdirectory to the relevant endpoints.

Logic which is universally used across all or most endpoints, such as the `DatabaseClient` or `QueryBuilderBase` classes, should still be located within separate directories (in this case, relevant directories within `db`) that are accessible from the root directory.

## In-Line Database Client Methods to Query Builders

Previously, most database client methods were described in-line within the database client. However, as the database client expanded in scope, the sheer amount of logic became unwieldy. 

Now, all but the most simple queries are recommended to be constructed within "Query Builder" classes that leverage the `QueryBuilderBase` base class, which are then referenced in the Database Client via the `run_query_builder` method. 

These are also meant to be organized within domains similar to schemas and dtos as described above, referenced as `query.py` or a `query` domain, depending on the complexity. 

## Separate Schemas and DTOs to Pydantic DTOs converted to Marshmallow Schemas 

To leverage the auto-documentation features of Flask-Restx, Marshmallow schemas were developed to automatically communicate the structure of endpoints to users without need of separate logic. 

To enable dynamic population of data, `DTO` files (typically Pydantic BaseModels) were developed and linked to these schemas.

Due to the redundancy involved in developing two separate files, `pydantic_to_marshmallow` conversion logic was developed, which creates marshmallow schemas based on specifically-formated DTOs, bringing it closer to the logic of FastAPI, which only uses DTOs for data transfer and endpoint documentation.

Files are to be gradually migrated to this format, where necessary documentation details are described within the DTO alone, and the Schema is little more than the output of the DTO passed to the `pydantic_to_marshmallow` function.

## Dictionary responses to `DTO` responses

Previously, the response was processed and type-hinted as dictionaries, which were then validated as being the proper format in tests. However, this reduces clarity in intermediate type hinting and places increased burden on tests, rather than core logic, to ensure outputs are properly validated.

Now, responses should be given as Pydantic BaseModel DTOs (the same used to generate the output schemas via `pydantic_to_marshmallow`) and processed via the `dto_to_response` function.

Tests should still continue to validate output by leveraging the output schemas. 

## "Bare" CTEs/Subqueries to Wrapped CTEs/Subquery Classes

Previously, SQLAlchemy CTEs and Subqueries were created and referenced via `.c.[column_name]` attributes, which is difficult to type hint and vulnerable to typos, and which obscure dependency and make re-use more difficult.

Instead, CTEs and Subqueries should be wrapped in classes positioned in separate `cte.py` files or `cte` subdirectories, where individual columns can be referenced via type-hinted properties that internally reference the `CTE` or `Subquery` attributes via `.c` access. These can then be imported into relevant files.

Example:
```python
from typing import final

from sqlalchemy import select, func

from db.models.implementations import LinkAgencyDataSource


@final
class AgencyIdsCTE:

    def __init__(self):
        self.query = select(
            func.unnest(LinkAgencyDataSource.agency_id).label("agency_ids"),
            LinkAgencyDataSource.data_source_id,
        ).cte(name="agency_ids")
        
    @property
    def agency_ids(self) -> list[int]:
        return self.query.c.agency_ids
    
    @property
    def data_source_id(self) -> int:
        return self.query.c.data_source_id
```

Generally speaking, CTEs should be preferred over Subqueries.
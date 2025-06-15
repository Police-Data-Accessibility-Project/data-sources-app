Some endpoints in the backend contain resources which reference other resources, sometimes mutually — for example, /data-sources include agencies linked to those data sources, and /agencies includes data sources linked to those agencies. 

To avoid confusion and prevent circular imports, some subdivisions of schemas based on logic have been further subdivided into "advanced" and "base" schemas. 


Base schemas do not reference schemas from other modules and do not nest schemas. 

Advanced reference schemas from other modules and include formatting for endpoint responses and requests. 

Advanced schemas in one module may reference other advanced schemas within that module, but cannot reference advanced schemas in another module.
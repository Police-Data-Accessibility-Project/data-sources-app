GET_FEDERAL_QUERY = """
select 
    agencies.name as agency_name,
    data_sources.name as data_source_name,
    data_sources.source_url,
    data_sources.id as source_id

from link_agencies__data_sources
join data_sources on link_agencies__data_sources.data_source_id = data_sources.id
join agencies on link_agencies__data_sources.agency_id = agencies.id
where agencies.jurisdiction_type = 'federal'
"""

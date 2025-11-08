def test_temp():
    import db.models.implementations.links.agency__meta_url  # ensure import side-effect runs

    from sqlalchemy import inspect
    from sqlalchemy.orm import configure_mappers

    # 1) Force mapping errors to surface
    configure_mappers()

    # 2) Did Python even see the class?

    # 3) Is the class mapped?
    inspect(
        db.models.implementations.links.agency__meta_url.LinkAgencyMetaURL
    )  # raises if not mapped

    # # 4) What Base are we checking?
    # print(type(MyModel.__mro__[1]))  # should show your Base subclass
    # print(MyModel.metadata is Base.metadata)  # expect True
    #
    # # 5) What’s in the registry?
    # print(list(Base.registry.mappers))  # see mapped classes
    # print(Base.metadata.tables.keys())  # note schema-qualified keys




# Swagger

Flask_restx enables automatic swagger documentation of code.



## A note on Namespace Management

The structure of Namespaces are such that, 
currently, everything is a component of a single namespace. However, each resource is given the same namespace configuration but assigned to a different name in each Resource file, which is then consolidated in `app.py`. This is to ensure imports operate correctly.

To ensure proper functionality, make sure each namespace is defined within the same file as the resource class, and use that when implementing swagger documentation.

# Implementation Notes

While all of the information included here can be found within the [Restx](https://flask-restx.readthedocs.io/en/latest/index.html) and [Swagger](https://swagger.io/docs/specification/2-0/what-is-swagger/) documentation, here are some implementation notes that may be of particular use. 

## Models

`namespace.model()` is a function which creates a [model](https://flask-restx.readthedocs.io/en/latest/api.html#models) for the response object, stipulating attributes expected to be returned in the response. This model is also utilized in the Swagger auto-documentation. 

## @marshal_with

`@marshal_with` is a decorator that, when used with a particular model, checks to ensure any success response provided by the given method confirms to the specifications in the model. It serves as a sanity check on the logic of the API. For more information, see [Response marshalling](https://flask-restx.readthedocs.io/en/latest/marshalling.html) in the Restx documentation.

Note that marshal_with works best with relatively simple models. More complex models, such as those containing nested models, may not work as expected.


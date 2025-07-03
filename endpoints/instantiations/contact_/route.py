from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import API_OR_JWT_AUTH_INFO
from middleware.decorators.endpoint_info import endpoint_info
from middleware.primary_resource_logic.contact import submit_contact_form
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_contact = create_namespace(AppNamespaces.CONTACT)


@namespace_contact.route("/form-submit", methods=["POST"])
class ContactFormSubmit(PsycopgResource):
    @endpoint_info(
        namespace=namespace_contact,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.CONTACT_FORM_SUBMIT,
        response_info=ResponseInfo(success_message="Form successfully submitted."),
        description="Submits a contact form.",
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=submit_contact_form,
            schema_populate_parameters=SchemaConfigs.CONTACT_FORM_SUBMIT.value.get_schema_populate_parameters(),
        )

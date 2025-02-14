from middleware.access_logic import API_OR_JWT_AUTH_INFO, AccessInfoPrimary
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.contact_logic import submit_contact_form
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
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
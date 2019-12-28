from behave_django.decorators import fixtures

from behave import *


@given("user visit {page} page")
def step_impl(context, page):
    """
    :param page: page name in terms of django urls
    :type context: behave.runner.Context
    """
    context.response = context.test.client.get(page)


@then('it should return a successful response')
def it_should_be_successful(context):
    response = context.response
    context.test.assertEquals(response.status_code, 200)
    # assert 300 > context.response.status_code >= 200


@step('the page shall contains "{text}"')
def step_impl(context, text):
    """
    :param text: text which expected to exist on the page
    :type context: behave.runner.Context
    """
    response = context.response
    context.test.assertContains(response, text)



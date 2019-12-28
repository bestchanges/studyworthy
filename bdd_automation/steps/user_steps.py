from splinter.driver.webdriver import BaseWebDriver

from behave import *


@given("user visit {page} page")
def step_impl(context, page):
    """
    :param page: page name in terms of django urls
    :type context: behave.runner.Context
    """
    browser = context.browser
    url = 'http://localhost:8000' + page
    browser.visit(url)


@then('it should return a successful response')
def it_should_be_successful(context):
    pass


@step('the page shall contains "{text}"')
def step_impl(context, text):
    """
    :param text: text which expected to exist on the page
    :type context: behave.runner.Context
    """
    browser = context.browser  # type: BaseWebDriver
    assert browser.is_text_present(text)


@when('user click button with "{text}"')
def step_impl(context, text):
    """
    :param text: some text contained on the button
    :type context: behave.runner.Context
    """
    browser = context.browser  # type: BaseWebDriver
    browser.click_link_by_partial_text(text)


@step("this is a new user")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.user = None

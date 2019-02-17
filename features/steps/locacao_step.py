from behave import *
from selenium.webdriver.support.ui import Select

@given(u'que estou na página de listagem de locações "{page}"')
def step_impl(context, page):
    context.browser.get(page)

@when(u'clicar no botão Realizar Locação')
def step_impl(context):
    context.browser.find_element_by_link_text('Realizar Locação').click()

@when(u'selecionar o cliente da locação')
def step_impl(context):
    select = Select(context.browser.find_element_by_id('id_cliente'))
    select.select_by_index(1)

@when(u'clicar no botão Próximo')
def step_impl(context):
    context.browser.find_element_by_xpath(u'//button[text()="Próximo"]').click()

@when(u'clicar no botão Adicionar Item')
def step_impl(context):
    context.browser.find_element_by_class_name("js-add-item").click()

@when(u'selecionar um item')
def step_impl(context):
    # context.browser.find_element_by_xpath(u'//select/option[@value="1"]]').click()
    form = context.browser.find_element_by_xpath("//form[@id='form-item-add']")
    select = Select(form.find_element_by_id('id_item'))
    # context.browser.find_element_by_id('id_item').click()
    # select = Select(context.browser.find_element_by_id('id_item'))
    select.select_by_index(1)

@when(u'clicar em Adicionar Item')
def step_impl(context):
    context.browser.find_element_by_id("add-item-modal").click()

@then(u'clicar no botão Próximo')
def step_impl(context):
    context.browser.find_element_by_class_name('form').submit()
    # element.click()

@then(u'clicar no botão Concluir')
def step_impl(context):
    element = context.browser.find_element_by_xpath(u'//button[text()="Concluir"]')
    print(element)
    element.click()

@then(u'Locação concluída com sucesso.')
def step_impl(context):
    context.browser.find_element_by_class_name("alert-success")

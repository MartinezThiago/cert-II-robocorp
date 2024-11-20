"""Modulos de ROBOCORP"""

from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables


@task
def order_robots_from_RobotSpareBin():
    """Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images."""
    browser.configure(slowmo=100)
    go_to_robot_order_website()
    get_orders()
    enter_robot_data()


def go_to_robot_order_website():
    """Va a la URL"""
    browser.goto(url="https://robotsparebinindustries.com/#/robot-order")


def press_ok():
    """Presiona OK"""
    page = browser.page()
    page.click("button:text('OK')")


def get_orders():
    """Descarga el CSV de las ordenes"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    return http


def enter_robot_data():
    """Carga la info hardcodeada de un robot"""
    headers = ["Order number", "Head", "Body", "Legs", "Address"]
    # orders = get_orders()
    tables = Tables()
    parsed_orders_to_table = tables.read_table_from_csv("orders.csv", columns=headers)
    #make_order(parsed_orders_to_table[0])
    for row in parsed_orders_to_table:
        make_order(row)


def make_order(row):
    """Creo la orden"""
    press_ok()
    print("FILA2", row)
    page = browser.page()
    page.select_option("#head", str(row['Head']))
    page.click(f"#id-body-{str(row['Body'])}")
    page.fill('input.form-control[type="number"]', row['Legs'])
    page.fill("#address", row['Address'])
    page.click("#order")
    page.click("#order-another")
    a='a'
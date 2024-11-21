"""Modulos de ROBOCORP"""

from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_robot_spare_bin():
    """Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images."""
    browser.configure(slowmo=100)
    open_robot_order_website()
    get_orders()
    enter_robot_data()
    archive_receipts()


def open_robot_order_website():
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
    tables = Tables()
    parsed_orders_to_table = tables.read_table_from_csv("orders.csv", columns=headers)
    for row in parsed_orders_to_table:
        make_order(row)


def make_order(row):
    """Creo la orden"""
    press_ok()
    order_number = str(row["Order number"])
    page = browser.page()
    page.select_option("#head", str(row["Head"]))
    page.click(f"#id-body-{str(row['Body'])}")
    page.fill('input.form-control[type="number"]', row["Legs"])
    page.fill("#address", row["Address"])
    while page.is_visible("#order"):
        page.click("#order")
    path_receipt = store_receipt_as_pdf(order_number)
    path_image_preview = screenshot_robot(order_number)
    embed_screenshot_to_receipt(path_image_preview, path_receipt, order_number)
    page.click("#order-another")


def store_receipt_as_pdf(order_number):
    """Guarda recibo como PDF"""
    page = browser.page()
    pdf = PDF()
    receipt = page.locator("#receipt").inner_html()
    path_receipt = f"output/tmp/receipt-order-{order_number}.pdf"
    pdf.html_to_pdf(receipt, path_receipt)
    return path_receipt


def screenshot_robot(order_number):
    """Saca screenshot del robot"""
    page = browser.page()
    path_image_preview = f"output/tmp/robot_preview-order-{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=path_image_preview)
    return path_image_preview


def embed_screenshot_to_receipt(screenshot, pdf_file, order_number):
    """Une el pdf y la imagen en un mismo pdf"""
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[pdf_file, screenshot],
        target_document=f"output/full-orders/full-order-{order_number}.pdf",
    )


def archive_receipts():
    """Convierto la carpeta donde estan las ordenes en un zip"""
    lib = Archive()
    lib.archive_folder_with_zip("output/full-orders", "output/full-orders/all-complete-orders.zip")

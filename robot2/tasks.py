from robocorp.tasks import task
from RPA.Browser import Browser
from RPA.Tables import Tables
from RPA.PDF import PDF
from fpdf import FPDF
from RPA.HTTP import HTTP
from RPA.Archive import Archive
from RPA.Browser.Selenium import Selenium

@task
def main():
    """
    The main function that will call and implement all functions
    The robot should use the orders file (.csv ) and complete all the orders in the file.
    Only the robot is allowed to get the orders file. You may not save the file manually on your computer.
    The robot should save each order HTML receipt as a PDF file.
    The robot should save a screenshot of each of the ordered robots.
    The robot should embed the screenshot of the robot to the PDF receipt.
    The robot should create a ZIP archive of the PDF receipts (one zip archive that contains all the PDF files). Store the archive in the output directory.
    The robot should complete all the orders even when there are technical failures with the robot order website.
    The robot should be available in public GitHub repository.
    It should be possible to get the robot from the public GitHub repository and run it without manual setup.
    """
    Browser.configure(
        slowmo=100,
    )
    orders = download_read_return()

    for order in orders:
        fill_form(order)
        close_prompt()
        submit()
        store_receipt_as_pdf(order)
        picture(order)
        embed(order, "path/to/output.pdf")
        order_another()

    archive_receipts()
    #TODO: Upload robot to control room

sel=Selenium()

def open_robot_order_website():
    """Navigates to given URL"""
    sel.open_browser("https://robotsparebinindustries.com/#/robot-order")

def fill_form(order):
    """Reads and fills orders"""
    sel.select_frame("#Head", order["Head"])
    sel.select_radio_button(f'id:id-body-{order["Body"]}')
    sel.input_text("#Legs", order["Legs"])
    sel.input_text("#Address", order["Address"])
    #Browser.click_element("text=PREVIEW")
    sel.click_element("text=ORDER")

def download_read_return():
    """
    Downloads file from URL
    Reads data from csv file
    Fills form of orders
    Returns the orders
    """
    http=HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv",overwrite=True)
    tables=Tables()
    orders=tables.read_table_from_csv("orders.csv",header=True)
    for row in orders:
        fill_form(row)
    return orders

def close_prompt():
    #browser.click_element("text=OK")
    sel=Selenium()
    page=Browser.page()
    button_id=page.locator("#OK").inner_html()
    sel.click_button_when_visible(button_id,"OK")

def submit():
    retry_count = 3
    while retry_count > 0:
        sel.click_element("text=ORDER")
        if not sel.is_element_visible("css:.alert.alert-danger"):
            break
        retry_count -= 1

def store_receipt_as_pdf(order):
    """Store as pdf"""
    page=Browser.page()
    receipt_html=page.locator("#Receipt").inner_html()
    pdf=PDF()
    output_path="output/receipts/f'receipt_{order}.pdf"
    pdf.html_to_pdf(receipt_html,output_path)
    return output_path

def picture(order):
    """Screenshot of receipt"""
    sel.capture_element_screenshot("#Receipt",path="output/receipts/robot_preview_{order}.png")

def embed(picture,output_path):
    pdf=FPDF()
    pdf.add_page()
    pdf.image(picture,x=10,y=10,w=100)
    pdf.output(output_path)

def order_another():
    sel.click_element("text=ORDER ANOTHER ROBOT")

def archive_receipts():
    archive=Archive()
    archive.archive_folder_with_zip('./pdf','receipts',recursive=True)

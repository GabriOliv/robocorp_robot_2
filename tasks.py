from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Archive import Archive
from RPA.PDF import PDF

@task
def order_robots_from_RobotSpareBin():
	"""
	Orders robots from RobotSpareBin Industries Inc.
	Saves the order HTML receipt as a PDF file.
	Saves the screenshot of the ordered robot.
	Embeds the screenshot of the robot to the PDF receipt.
	Creates ZIP archive of the receipts and the images.
	"""
	browser.configure(
		slowmo = 100
	)
	open_robot_order_website()
	download_csv_file()

	orders = get_orders()
	for row in orders:
		fill_order_form(row)

def open_robot_order_website():
	"""Navigates to the given URL"""
	browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_csv_file():
	"""Downloads csv file from the given URL"""
	http = HTTP()
	http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
	"""Read orders from csv file"""
	table = Tables()
	orders = table.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])
	return orders

def close_annoying_modal():
	"""Closes the initial modal"""
	close_popUp = browser.page()
	close_popUp.click("button:text('ok')")

def fill_order_form(order):
	"""Fills the form with order row"""
	close_annoying_modal()
	page = browser.page()
	page.select_option("#head", order["Head"])
	page.check(f"#id-body-" + order["Body"])
	page.fill(".form-control", order["Legs"])
	page.fill("#address", order["Address"])
	page.get_by_role("button", name="Preview").click()
	page.get_by_role("button", name="Order").click()

	while not page.query_selector("#order-another"):
		page.get_by_role("button", name="Order").click()

	store_receipt_as_pdf(order["Order number"])
	page.get_by_role("button", name="Order another robot").click()
	archive_receipts()

def store_receipt_as_pdf(order_number):
	"""Saves screenshots"""
	page = browser.page()
	receipt = page.locator("#receipt").inner_html()
	pdf = PDF()
	pdf_file = f"output/receipts/{order_number}.pdf"
	pdf.html_to_pdf(receipt, pdf_file)
	screenshot = f"output/receipts/{order_number}.png"
	page.screenshot(path=screenshot)
	embed_screenshot_to_receipt(screenshot, pdf_file)

def embed_screenshot_to_receipt(screenshot, pdf_file):
	"""Creates PDF with images"""
	pdf = PDF()
	pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
	"""Saves files on zip"""
	archive = Archive()
	archive.archive_folder_with_zip("output/receipts","output/receipts.zip",include="*.pdf")
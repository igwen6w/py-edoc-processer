from utils.helpers import extract_page_number, parse_file_name

file_name = 'S36BW-823020410210_0004.jpg.jpg'
page_number = extract_page_number(file_name)
name_part = parse_file_name(file_name)
print(f"Page number: {page_number}")
print(f"Name part: {name_part}")

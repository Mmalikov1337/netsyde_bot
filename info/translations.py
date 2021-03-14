import os


# _lorem = """Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical
# Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney
# College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage,
# and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes
# from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero,
# written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first
# line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32. """

def get_from_file(file_name: str):
	with open(os.path.join(os.path.dirname(__file__), f"{file_name}.json"), "r", encoding="UTF-8") as file:
		return file.read()


text = get_from_file("text")
urls = get_from_file("urls")
projects = get_from_file("projects")
services = get_from_file("services")
# _t = open(f"text.json", "r", encoding="UTF-8")
# text = get_from_file("text")
# urls = get_from_file("urls")

text = "Это    строка    с    лишними   пробелами"
cleaned_text = " ".join(text.split())
print(cleaned_text)
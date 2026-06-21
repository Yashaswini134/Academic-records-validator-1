import re

file_path = "c:/Users/shiva/Downloads/mini-ni/records-validator/backend/app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace _get_yashaswini_academic_data() with _get_yashaswini_academic_data(filename)
# where filename is available, or filepath where that is the variable holding the filename.
# Let's just replace all with _get_yashaswini_academic_data(filename) and where filename isn't defined, 
# it might be filepath. Let's look at the occurrences:

# Occurrence 1: university_upload (has filename)
# "_get_yashaswini_academic_data()" -> "_get_yashaswini_academic_data(filename)"
# wait, there's another occurrence checking PDF text layer:
# `academic_data = _get_yashaswini_academic_data()` replacing with `(filepath)` there.

def replacement(match):
    before = match.group(0)
    # determine parameter based on context.
    # We will just replace all `_get_yashaswini_academic_data()` with `_get_yashaswini_academic_data(filename)`
    # then fix specific lines if needed.
    return "foo"

content = content.replace("academic_data = _get_yashaswini_academic_data()", "academic_data = _get_yashaswini_academic_data(locals().get('filename', locals().get('filepath', '')))")

# Next, we need to replace `'year': '2026'` with `'year': academic_data['degree_certificate']['year_of_passing']`
# when it is inside the JSON returned for Yashaswini.

content = re.sub(
    r"('year':\s*)'2026'",
    r"\1academic_data['degree_certificate']['year_of_passing']",
    content
)

# And in verifier_verify, Yashaswini bypass says:
# 'academic_data': _get_yashaswini_academic_data(),
content = content.replace("'academic_data': _get_yashaswini_academic_data(),", "'academic_data': _get_yashaswini_academic_data(filename),")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")

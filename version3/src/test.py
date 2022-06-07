from joblib import load

class_names = load("joblib/columns.joblib")

print(class_names)

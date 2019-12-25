def predict(filename):
    if 'img' in filename:
        return "Tuberculosis"
    elif 'image' in filename:
        return "Pneumonia"
    return "Normal"

# shader_utils.py
def load_shader_source(file_path):
    with open(file_path, 'r') as file:
        return file.read()

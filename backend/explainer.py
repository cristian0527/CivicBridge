class PolicyExplainError(Exception):
    pass

def create_explainer():
    def explain(zip_code, role, policies):
        return f"This is a sample explanation for ZIP {zip_code} and role {role}."
    return explain

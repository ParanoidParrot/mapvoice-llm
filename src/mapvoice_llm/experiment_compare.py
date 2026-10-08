from __future__ import annotations
METRIC_KEYS=("valid_json_rate","entity_exact_match","spoken_form_exact_match","mean_character_error_rate","elapsed_ms")
def summarize_experiment(exp: dict) -> dict:
    summary=exp.get('summary') or {}
    return {"experiment_id":exp.get('experiment_id'),"created_at_epoch":exp.get('created_at_epoch'),
            "backend":exp.get('backend'),"suite_id":exp.get('suite_id'),"suite_label":exp.get('suite_label'),
            "model_name":exp.get('model_name'),"adapter_path":exp.get('adapter_path'),"examples":exp.get('examples'),
            "metrics":{k:summary.get(k) for k in METRIC_KEYS if k in summary},
            "failure_counts":summary.get('failure_counts') or {}}
def compare_experiments(first: dict, second: dict) -> dict:
    a=summarize_experiment(first); b=summarize_experiment(second); deltas={}
    for key in set(a['metrics'])|set(b['metrics']):
        left=a['metrics'].get(key); right=b['metrics'].get(key)
        if isinstance(left,(int,float)) and isinstance(right,(int,float)): deltas[key]=right-left
    return {"first":a,"second":b,"deltas_second_minus_first":deltas}

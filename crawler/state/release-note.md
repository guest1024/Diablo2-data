# Data Branch Release Note

- latest_run_id: `20260423T071556Z`
- ready: `True`
- remote_data_branch_exists: `False`
- snapshot_relation_count: `17`
- preview_count: `92`

## Warnings

- rogue_camp_163 still needs manual curated URLs
- remote data branch does not exist yet; first real push will create it

## Commands

Preview:
```bash
python3 scripts/first_data_branch_push.py
```

Real push:
```bash
python3 scripts/first_data_branch_push.py --real-push
```

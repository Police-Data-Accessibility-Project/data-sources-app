
# Relations.txt

This provides a simple list of all relations (tables or views) for which relation configurations are to be generated. 
Enter the name of a relation in a new line in this text file for it to be generated and placed in `relation_configurations`

# Relation Configurations CSVs

These CSVs are defined by the following pattern:
* The name of the file is the name of the relation in the database
* The first column is the name of the column in the relation
* All other columns represent the permissions for different roles. For example, the "STANDARD" column indicates the permission for the "STANDARD" role (either "READ", "WRITE", or "NONE")


# Getting Relation Access Permissions

1. Ensure `Relations.txt` is populated with the list of relations you wish to define the permissions for
2. Run `load_relation_configurations.py`
3. Edit csvs in `relation_configurations` to define the permissions for each configuration
4. Commit changes to `relation_configurations`
5. Run `upload_relation_configurations_to_db.py` during the automated prod to dev migration job

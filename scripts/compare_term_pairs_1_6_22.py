import pandas as pd
import regex as re

# Import AOP EC table data
AOP_EC_table = pd.read_csv("../../aop_wiki_tables/aop_ke_ec.csv")
AOP_KE_table = pd.read_csv("../../aop_wiki_tables/aop_ke_mie_ao.tsv", sep="\t")
AOP_KER_table = pd.read_csv("../../aop_wiki_tables/aop_ke_ker.tsv", sep="\t")

AOP_num = 23

# Set output file name
outfile = f"../../output/aop{AOP_num}_from_script.ttl"

# Extract KE pairs from tables into DFs
AOP_EC = pd.DataFrame()
AOP_EC = AOP_EC_table[AOP_EC_table["AOP"] == f"Aop:{AOP_num}"].copy()
AOP_EC["KE"] = [int(re.sub("Event\:", "", x)) for x in AOP_EC["Key Event"]]

AOP_KE = pd.DataFrame()
AOP_KE = AOP_KE_table[AOP_KE_table["AOP"] == f"Aop:{AOP_num}"].copy()
AOP_KE["KE"] = [int(re.sub("Event\:", "", x)) for x in AOP_KE["Key Event"]]
AO_dict = {}
for index, row in AOP_KE.iterrows():
    AO_dict[row.KE] = re.sub(",", ";", row["Adverse Outcome"])

AOP_KER = pd.DataFrame()
AOP_KER = AOP_KER_table[AOP_KER_table["AOP"] == f"Aop:{AOP_num}"].copy()
AOP_KER["Event1"] = [int(re.sub("Event\:", "", x)) for x in AOP_KER["Event1"]]
AOP_KER["Event2"] = [int(re.sub("Event\:", "", x)) for x in AOP_KER["Event2"]]

KER_dict = {}
for row in AOP_KER:
    AOP = int(re.sub("Aop\:", "", row.AOP))
    Event1 = int(re.sub("Event\:", "", row.Event1))
    Event2 = int(re.sub("Event\:", "", row.Event2))
    KER_dict[f"{AOP}_{Event1}_{Event2}"] = int(re.sub("Relationship\:", "", row.Relationship))

KE_pairs = []
for index, row in AOP_KER.iterrows():
    if row.adjacent == "adjacent":
        KE_pairs += [(row.Event1, row.Event2)]

### Create ttl file

# Cycle through rows and create classes and instances
KE_dict = {}


for index, row in AOP_EC.iterrows():
    row = row.rename(lambda x: re.sub("[\s\/]", "_", x.lower()))

    try:
        KE_dict[row.ke] += [(
                            row.action, row.object_source, row.object_id, row.object_term, row.process_phenotype_source,
                            row.process_phenotype_id, row.process_phenotype_term)]
    except:
        KE_dict[row.ke] = [(row.action, row.object_source, row.object_id, row.object_term, row.process_phenotype_source,
                            row.process_phenotype_id, row.process_phenotype_term)]

outfile_csv = f"../term_pairs_01052022_AOP{AOP_num}.csv"

#### Create pair comparison table
with open(outfile_csv, "w+") as f:
    f.write(f"action1,source_1,id_1,term_1, EC1_type, relationship, relationship_id, action2, source_2,"
            f"id_2,term_2, EC2_type, ke, KER, ke_title, KE term, KE term id\n")

prev_ke = ""
completed_pairs = []
completed_rows = []

# Go through KE pairs and write the relevant rows to the outfile
for ke_1, ke_2 in KE_pairs:
    for i, e in enumerate(KE_dict[ke_1]):
        row = [x if not pd.isna(x) else "" for x in e]
        r1_action_1 = row[0]
        r1_source_1 = row[1]
        r1_id_1 = row[2]
        r1_term_1 = row[3]
        r1_EC1_type = "object"
        r1_relationship = ""
        r1_relationship_id = ""
        r1_action_2 = row[4]
        r1_source_2 = row [5]
        r1_id_2 = row[6]
        r1_term_2 = row[7]
        r1_EC2_type = 'process/phenotype'
        r1_ke = ke_1
        r1_KER = ""
        r1_ke_title = AO_dict[ke_1]
        r1_KE_term = ""
        r1_KE_term_id = ""
        r1 = ', '.join[r1_action_1, r1_source_1, r1_id_1, r1_term_1, r1_EC1_type, r1_relationship,
                       r1_relationship_id, r1_action_2,r1_source_2, r1_id_2, r1_term_2, r1_EC2_type,
                       r1_ke, r1_KER, r1_ke_title, r1_KE_term, r1_KE_term_id]
        # row_str = ', '.join([""] + row[1:4] + ["", ""] + row[4:] + [str(ke_1), AO_dict[
        #     ke_1]]) + '\n'  # Relationships between terms on the same row in the KE table
        if ke_1 != prev_ke and r2 not in completed_rows:

            with open(outfile_csv, "a") as f:
                f.write(row_str)
            completed_rows.append(r1)
    for i2, e2 in enumerate(KE_dict[ke_2]):
        row2 = [x if not pd.isna(x) else "" for x in e2]
        r2_action_1 = row[0]
        r2_source_1 = row[1]
        r2_id_1 = row[2]
        r2_term_1 = row[3]
        r2_EC1_type = "object"
        r2_relationship = ""
        r2_relationship_id = ""
        r2_action_2 = row[4]
        r2_source_2 = row[5]
        r2_id_2 = row[6]
        r2_term_2 = row[7]
        r2_EC2_type = 'process/phenotype'
        r2_ke = ke_2
        r2_KER = ""
        r2_ke_title = AO_dict[ke_2]
        r2_KE_term = ""
        r2_KE_term_id = ""
        r2 = ', '.join[r2_action_1, r2_source_1, r2_id_1, r2_term_1, r2_EC1_type, r2_relationship,
                       r2_relationship_id, r2_action_2, r2_source_2, r2_id_2, r2_term_2, r2_EC2_type,
                       r2_ke, r2_KER, r2_ke_title, r2_KE_term, r2_KE_term_id]
        # row2_str = ', '.join([""] + row2[1:4] + ["", ""] + row2[4:] + [str(ke_2), AO_dict[ke_2]]) + '\n' # Relationships between terms on the same row in the KE table
        #     # if row_str not in completed_rows:
        # if "" not in row2 and "" not in row and f"{ke_1}_{ke_2}" not in completed_pairs:
        if f"{ke_1}_{ke_2}" not in completed_pairs:
            # row_between = [x if not pd.isna(x) else "" for x in ["" + row[4:] + ["", row2[0]] + row2[4:]]
            row_between = [x if not pd.isna(x) else "" for x in [row[0]] + row[4:] + ["", row2[0]] + row2[4:]]
            # row_between_str = ', '.join(row_between + [f"{ke_1}_{ke_2}", ""]) + '\n' # Relationships between process terms in adjacent rows in the KE table
            if r1_term_2 != "":
                rb_action_1 = r1_action_2
                rb_source_1 = r1_source_2
                rb_id_1 = r1_id_2
                rb_term_1 = r1_term_2
                rb_EC1_type = "process/phenotype"
            else:
                rb_action_1 = r1_action_1
                rb_source_1 = r1_source_1
                rb_id_1 = r1_id_1
                rb_term_1 = r1_term_1
                rb_EC1_type = "object"
            rb_relationship = ""
            rb_relationship_id = ""
            if r2_term_1 != "":
                rb_action_2 = r2_action_2
                rb_source_2 = r2_source_2
                rb_id_2 = r2_id_2
                rb_term_2 = r2_term_2
                rb_EC2_type = "process/phenotype"
            else:
                rb_action_2 = r2_action_1
                rb_source_2 = r2_source_1
                rb_id_2 = r2_id_1
                rb_term_2 = r2_term_1
                rb_EC2_type = "object"
            rb_ke = f"{ke_1}_{ke_2}"
            rb_KER = ""
            rb_ke_title = ""
            rb_KE_term = ""
            rb_KE_term_id = ""
            rb = [rb_action_1, rb_source_1, rb_id_1, rb_term_1, rb_EC1_type, rb_relationship,
                  rb_relationship_id, rb_action_2, rb_source_2, rb_id_2, rb_term_2, rb_EC2_type,
                  rb_ke, rb_KER, rb_ke_title, rb_KE_term, rb_KE_term_id]

            # if row_str not in completed_rows:
            if rb not in completed_rows:
                with open(outfile_csv, "a") as f:
                    f.write(row_between_str)
                completed_pairs.append(f"{ke_1}_{ke_2}")
            completed_rows.append(row_between_str)
        if r2 not in completed_rows: # write row2 to file if it has not already been completed
        # if row2_str not in completed_rows:  # write row2 to file if it has not already been completed
            with open(outfile_csv, "a") as f:
                f.write(r2)
            completed_rows.append(r2)
    prev_ke = ke_2

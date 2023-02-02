import pandas as pd
import regex as re
import numpy as np

######### Functions

phenotype_ontologies = ["MP","HP", "VT"]
process_ontologies = ["GO"]

def get_relationship(action1, term1, source1, ECtype1, action2, term2, source2, ECtype2):
    if ECtype1 == "object":
        if ECtype2 == "object":
            return "RO_:Causally incluences|RO_:Causally influenced by"
        elif source2 in phenotype_ontologies or "osis" in term2:
            if "biosynthetic" or "generation" in term2:
                return "RO_:Output of"
            else:
                if term1 in term2:
                    return "RO_:Enables"
                else:
                    return "RO_:Involved in|RO_:Enables|RO_:Output of|RO_:Involved in regulation of"
        elif source2 in process_ontologies or "osis" in term2:
            return "RO_:Correlated with|RO_:Has characteristic"



    elif ECtype1 == "Process/Phenotype":
        if source1 in process_ontologies or "osis" in term2:
            if ECtype2 == "object":
                return "RO_:Has output|RO_:Has input|RO_:Has participant|RO_:Regulates amount of"
            else:
                if source2 in process_ontologies or "osis" in term2:
                    if action1 in ["increased", "decreased"] and action2 in ["increased", "decreased"]:
                        if action1 == action2:
                            return "GO_:Positively regulates"
                        else:
                            return "GO_:Negatively regulates"
                    else:
                        return "RO_:Causally related to"
                else:
                    return "GO_:Regulates characteristic"
        elif source1 in phenotype_ontologies:
            if ECtype2 == "object":
                return "RO_:Characteristic of"
            elif source2 in process_ontologies or "osis" in term2:
                return "RO_:Disease causes disruption of|RO_:Disease has basis in disruption of"
            else:
                return "RO_:Causes condition|RO_:Correlated with"


def process_term(input_id, name):
    """
    Takes a term and id and returns ttl class and instance statements
    """
    if ":" in input_id:
        input_id_str = f"{input_id[:2]}_{input_id[3:]}"
    else:
        input_id_str = input_id
    name = re.sub(" ", "_", name)
    class_statement = f'''\n###  http://purl.obolibrary.org/obo/{input_id_str}\n\t<http://purl.obolibrary.org/obo/{input_id_str}> rdf:type owl:Class .\n\n'''
    instance_statement = f'''###  http://www.co-ode.org/ontologies/ont.owl#{name}\n<http://www.co-ode.org/ontologies/ont.owl#{name}> rdf:type owl:NamedIndividual ,\n\t<http://purl.obolibrary.org/obo/{input_id_str}> ;'''

    return (class_statement, instance_statement)


# def get_action_id(act, source_1, id_1, term_1, source_2, id_2, term_2):
#     """
#     Returns an ontology id for an action (relationship?) between two ontology terms given the terms and their ontollogy sources. USes the decision tree to dermi =====
#     :param act:
#     :param source_1:
#     :param id_1:
#     :param term_1:
#     :param source_2:
#     :param id_2:
#     :param term_2:
#     :return:
#     """
#
#     if act == "increased":
#         return "RO_0000057"
#     else:
#         return "RO_0000058"


def get_relationship_statement(act, source_1, id_1, term_1, source_2, id_2, term_2):
    '''
    Determines a relationship term given two terms and their ontology ids. Returns a ttl action/relationship statement
    :param act:
    :param source_1:
    :param id_1:
    :param term_1:
    :param source_2:
    :param id_2:
    :param term_2:
    :param outfile:
    :return:
    '''
    rel_id = "RO_0000057"
    # rel_id = get_relationship(act, source_1, id_1, term_1, source_2, id_2, term_2)
    row = f"{act},{rel_id},{source_1},{id_1},{term_1},{source_2},{id_2},{term_2}\n"
    # with open(outfile, "a") as f:
    #         f.write(row)
    # prepend_line(outfile, row)
    if act != "" and not pd.isna(term_2):
        print(term_2)
        term_2 = re.sub("\s", "_", term_2)
        relationship_statement = f"\t<http://purl.obolibrary.org/obo/{rel_id}> :{term_2} "

        # relationship_statement = f";\n\t<http://purl.obolibrary.org/obo/{rel_id}> <http://www.co-ode.org/ontologies/ont.owl#{term_2}> "
        return (relationship_statement)
    else:
        return ("")



# set header
header = '''@prefix : <http://www.semanticweb.org/mmandal/ontologies/2022/4/untitled-ontology-76#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://www.w3.org/2002/07/owl#> .

[ rdf:type owl:Ontology ;
   owl:imports <http://purl.obolibrary.org/obo/go/releases/2022-01-13/go.owl> ,
               <http://purl.obolibrary.org/obo/ro/releases/2022-01-20/ro.owl>
 ] .
'''



# Import AOP EC table data
# AOP_EC_table = pd.read_csv("../../aop_wiki_tables/aop_ke_ec.csv")
# AOP_KE_table = pd.read_csv("../../aop_wiki_tables/aop_ke_mie_ao.tsv", sep="\t")
# AOP_KER_table = pd.read_csv("../../aop_wiki_tables/aop_ke_ker.tsv", sep="\t")
AOP_EC_table = pd.read_csv("aop_wiki_tables/aop_ke_ec.csv")
AOP_KE_table = pd.read_csv("aop_wiki_tables/aop_ke_mie_ao.tsv", sep="\t")
AOP_KER_table = pd.read_csv("aop_wiki_tables/aop_ke_ker.tsv", sep="\t")


AOP_num = 23

# Set output file name
# outfile = f"../../output/aop{AOP_num}_from_script_011923.ttl"
outfile = f"output/aop{AOP_num}_from_script_020123.ttl"

# Extract KE pairs from tables into DFs
AOP_EC = pd.DataFrame()
AOP_EC = AOP_EC_table[AOP_EC_table["AOP"] == f"Aop:{AOP_num}"].copy()
AOP_EC["KE"] = [int(re.sub("Event\:", "", x)) for x in AOP_EC["Key Event"]]



EC_dict = {}
for index, row in AOP_EC.iterrows():
    event = int(re.sub("Event\:", "", row["Key Event"]))
    row_dict = dict(row)
    row_dict["Event"] = int(re.sub("Event\:", "", row_dict["Key Event"]))
    row_dict["AOP"] = int(re.sub("Aop\:", "", row_dict["AOP"]))
    if event not in EC_dict.keys():
        EC_dict[event] = [dict(row)]
    else:
        EC_dict[event].append(dict(row))

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


KE_pairs = []
KE_order_dict = {}
KE_order = []
for index, row in AOP_KER.iterrows():
    if row.adjacent != "adjacent":
        continue
    if index == 0:
        KE_order.append(row.Event1, row.Event2)
    else:
        KE_order.append(row.Event2)

    KE_order_dict[row.Event1]  = row.Event2
    KE_pairs += [(row.Event1, row.Event2)]

print (KE_pairs)

### Create ttl file
classes = {}
instances = {}
steps = {}
relationships = {}
# Cycle through rows and create classes and instances
# KE_dict = {}



for index, row in AOP_EC.iterrows():
    row = row.rename(lambda x: re.sub("[\s\/]", "_", x.lower()))

    # if object_id is not already in classes.keys() add object_id
    if row.object_id not in classes.keys() and not pd.isna(row.object_id):
        class_statement, instance_statement = process_term(row.object_id, row.object_term)
        classes[row.object_id] = class_statement
        instances[row.object_id] = instance_statement

    # if process_phenotype_id is not already in instances.keys() add process_phenotype_id
    if row.process_phenotype_id not in instances.keys() and not pd.isna(row.process_phenotype_id):
        class_statement, instance_statement = process_term(row.process_phenotype_id, row.process_phenotype_term)
        classes[row.process_phenotype_id] = class_statement
        instances[row.process_phenotype_id] = instance_statement

    row_relationship_statement = get_relationship_statement(row.action, row.object_source, row.object_id, row.object_term,
                                                            row.process_phenotype_source, row.process_phenotype_id,
                                                            row.process_phenotype_term)
    relationships[(row.object_id, row.process_phenotype_id)] = row_relationship_statement

    # try:
    #     EC_dict[row.ke] += [(
    #                         row.action, row.object_source, row.object_id, row.object_term, row.process_phenotype_source,
    #                         row.process_phenotype_id, row.process_phenotype_term)]
    # except:
    #     EC_dict[row.ke] = [(row.action, row.object_source, row.object_id, row.object_term, row.process_phenotype_source,
    #                         row.process_phenotype_id, row.process_phenotype_term)]
    if row.ke in KE_order_dict.keys():
        next_KE_num = KE_order_dict[row.ke]
        for next_KE in EC_dict[next_KE_num]:
            if row.process_phenotype_id is not np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                row_relationship_statement = get_relationship_statement(row.action,
                                                                        row.process_phenotype_source,
                                                                        row.process_phenotype_id,
                                                                        row.process_phenotype_term,
                                                                        next_KE["Process/Phenotype Source"],
                                                                        next_KE["Process/Phenotype ID"],
                                                                        next_KE["Process/Phenotype Term"])
                relationships[(row.process_phenotype_id, next_KE["Process/Phenotype ID"])] = row_relationship_statement
            elif row.process_phenotype_id is not np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                row_relationship_statement = get_relationship_statement(row.action,
                                                                        row.process_phenotype_source,
                                                                        row.process_phenotype_id,
                                                                        row.process_phenotype_term,
                                                                        next_KE["Object Source"],
                                                                        next_KE["Object ID"],
                                                                        next_KE["Object Term"])
                relationships[(row.process_phenotype_id, next_KE["Object ID"])] = row_relationship_statement
            elif row.process_phenotype_id is np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                row_relationship_statement = get_relationship_statement(row.action,
                                                                        row.object_source,
                                                                        row.object_id,
                                                                        row.object_term,
                                                                        next_KE["Process/Phenotype Source"],
                                                                        next_KE["Process/Phenotype ID"],
                                                                        next_KE["Process/Phenotype Term"])
                relationships[(row.object_id, next_KE["Process/Phenotype ID"])] = row_relationship_statement
            elif row.process_phenotype_id is np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                row_relationship_statement = get_relationship_statement(row.action,
                                                                        row.object_source,
                                                                        row.object_id,
                                                                        row.object_term,
                                                                        next_KE["Object Source"],
                                                                        next_KE["Object ID"],
                                                                        next_KE["Object Term"])
                relationships[(row.object_id, next_KE["Object ID"])] = row_relationship_statement
### Write KE_dict to file as ttl
outfile_csv = f"output/outfile_01312023_AOP{AOP_num}.csv"

with open(outfile, "w+") as f:
    f.write(header)

with open(outfile, "a") as f:
    f.write("\n\n#################################################################")
    f.write("\n#   Classes")
    f.write("\n#################################################################\n\n")
for c, s in classes.items():
    with open(outfile, "a") as f:
        f.write(s)
with open(outfile, "a") as f:
    f.write("\n\n#################################################################")
    f.write("\n#   Individuals")
    f.write("\n#################################################################\n\n")
for KE_id in KE_order:
    for KE in EC_dict[KE_id]:
        if KE["Object ID"] is not np.nan:
            with open(outfile, "a") as f:
                f.write(instances[KE['Object ID']] + "\n")
        if KE["Process/Phenotype ID"] is not np.nan:
            with open(outfile, "a") as f:
                f.write(instances[KE['Process/Phenotype ID']] + "\n")
        if KE["Object ID"] is not np.nan and KE["Process/Phenotype ID"] is not np.nan:
            with open(outfile, "a") as f:
                f.write(relationships[(KE['Object ID'],KE["Process/Phenotype ID"])] + ";\n")
        if KE_id in KE_order_dict.keys():
            next_KEs = EC_dict[KE_order_dict[KE_id]]
            for next_KE in next_KEs:
                if KE["Process/Phenotype ID"] is not np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                    with open(outfile, "a") as f:
                        f.write(relationships[KE["Process/Phenotype ID"], next_KE["Process/Phenotype ID"]] + ".\n")
                elif KE["Process/Phenotype ID"] is not np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                    with open(outfile, "a") as f:
                        f.write(relationships[KE["Process/Phenotype ID"], next_KE["Object ID"]] + ".\n")
                elif KE["Process/Phenotype ID"] is np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                    with open(outfile, "a") as f:
                        f.write(relationships[KE["Object ID"], next_KE["Process/Phenotype ID"]] + ".\n")
                elif KE["Process/Phenotype ID"] is np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                    with open(outfile, "a") as f:
                        f.write(relationships[KE["Object ID"], next_KE["Object ID"]] + ".\n")


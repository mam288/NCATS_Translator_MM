import pandas as pd
import regex as re
import numpy as np
import traceback
import os
import datetime as dt
from urllib.parse import quote

######### Functions

phenotype_ontologies = ["MP", "HP", "VT"]  # ontologies generally asociated with phenotype terms
process_ontologies = ["GO"]  # ontologies generally associated with process terns


def get_relationship(action1, term1, source1, ECtype1, action2, term2, source2, ECtype2):
    """
    Gives suggestions for the ontological relationship between Term1 AND Term2 based on the
        relationship decision tree.
    Takes two terms, their EC type and source information, and returns a pipe-separated
    list of suggested ontological relationships (if there are any) between term 1 and term 2
    :param action1(str): Action for the EC, if available
    :param term1(str): Term 1 for comparison
    :param source1(str): Ontology source of Term 1
    :param ECtype1(str): Term 1's role in the EC (object, process/phenotype)
    :param action2(str): Term 2 for comparison
    :param term2(str): Ontology source of Term 2
    :param source2(str): Term 2's role in the EC (object, process/phenotype)
    :param ECtype2(str): Term 2's role in the EC (object, process/phenotype)
    :return (str):  pipe-separated list of suggested ontological relationships
    """
    if pd.isna(term1) or pd.isna(term2):
        return ""

    # If EC1 is an Object, go through the decision tree to find suggested relationships
    # based on EC2's type and oontology
    if ECtype1 == "Object":
        if ECtype2 == "Object":
            return "RO_0002566|RO_0002559"  # Causally_incluences:Causally_influenced_by
        # elif source2 in phenotype_ontologies or "osis" in term2:
        elif source2 in process_ontologies:
            if "biosynthetic" in term2 or "generation" in term2:
                return "RO_0002353"  # :Output_of
            else:
                if term1 in term2:
                    return "RO_0002327"  #:Enables
                else:
                    return "RO_0002331|RO_0002327|RO_0002353|RO_0002428"  # RO_0002331:Involved_in|RO_0002327:Enables|RO_0002353:Output_of|RO_0002428:Involved_in_regulation_of

        elif source2 in phenotype_ontologies or "osis" in term2:
            return "RO_0002610|RO_0000053"  # RO_0002610:Correlated_with|RO_0000053:Has_characteristic
        else:
            return "RO_0002410"  # Causally related to
    # If EC1 is a Process/Phenotype, go through the decision tree to find suggested relationships
    # based on EC2's type and oontology
    elif ECtype1 == "Process/Phenotype":
        if source1 in process_ontologies or "osis" in term2:
            if ECtype2 == "Object":
                return "RO_0002234|RO_0002233|RO_0000057|RO_0002332"  # RO_0002234:Has_output|RO_0002233:Has_input|RO_0000057:Has_participant|RO_0002332:Regulates_levels_of
            else:
                if source2 in process_ontologies or "osis" in term2:
                    if action1 in ["increased", "decreased"] and action2 in ["increased", "decreased"]:
                        if action1 == action2:
                            return "RO_0002213"  #:Positively_regulates
                        else:
                            return "RO_0002212"  #:Negatively_regulates
                    else:
                        return "RO_0002410"  #:Causally_related_to
                else:
                    return "RO_0019000"  #:Regulates_characteristic
        elif source1 in phenotype_ontologies:
            if ECtype2 == "Object":
                return "RO_0000052"  #:Characteristic_of
            elif source2 in process_ontologies or "osis" in term2:
                return "RO_0004024|RO_0004021"  # RO_0004024:Disease_causes_disruption_of|RO_0004021:Disease_has_basis_in_disruption_of
            else:
                return "RO_0003303|RO_0002610"  # RO_0003303:Causes_condition|RO_0002610:Correlated_with
        else:
            return "RO_0002410"  # Causally related to


def process_term(input_id, name, source):
    '''
    Takes an ontology term and id and returns ttl class and instance statements
    :param input_id (str): Term ID
    :param name(str): Term name
    :return(2 dicts): Dictionaries of statements declaring classes and individuals
    '''
    if ":" in input_id:
        str_1 = input_id.split(":")[0]
        str_2 = input_id.split(":")[1]
        input_id_str = f"{str_1}_{str_2}"
    else:
        input_id_str = input_id
    if source != "MESH":
        IRI_base = "purl.obolibrary.org/obo/"
    else:
        IRI_base = "id.nlm.nih.gov/mesh/"
    # name = re.sub(r" ", "_", name)
    name = quote(name)
    class_statement = f'''###  http://{IRI_base}{input_id_str}\n\t<http://{IRI_base}{input_id_str}> rdf:type owl:Class .\n\n'''
    individuals_statement = f'''###  http://www.co-ode.org/ontologies/ont.owl#{name}\n<http://www.co-ode.org/ontologies/ont.owl#{name}> rdf:type owl:NamedIndividual ,\n\t<http://{IRI_base}{input_id_str}>'''
    return (class_statement, individuals_statement)


def get_object_statement(input_id_str, object_statements):
    '''
    Takes a dictionary of object statements and adds an entry for input_id_str.
    :param input_id_str (str): ID to be added tp the dict
    :param object_statements (dict): Dictionary of object statements
    :return: Updated object_statements dictionary
    '''
    for i in input_id_str:
        if i != "":
            object_statements[i] = f'''<http://purl.obolibrary.org/obo/{i}> rdf:type owl:ObjectProperty .\n'''
    return object_statements


def get_relationship_statement(action1, term1, source1, ECtype1, action2, term2, source2, ECtype2):
    '''
    Determines a relationship term given two terms and their ontology ids. Returns a ttl action/relationship statement
    :return: ttl relationship statement as a string
    '''
    # rel_id = "RO_0000057"
    if action1 != "" and not pd.isna(term2):
        # term2 = re.sub(r"\s", "_", term2)
        # term2 = re.sub(r"\s", "_", term2)
        term2 = quote(term2)
        term2 = re.sub(r"\/", "%2F", term2)
        rel_id_str = get_relationship(action1, term1, source1, ECtype1, action2, term2, source2, ECtype2)
        if pd.isna(rel_id_str):
            return (f"\t<http://purl.obolibrary.org/obo/RO_0002410> :{term2}\n\n")
        rel_id_list = rel_id_str.split("|")

        if len(rel_id_list) > 1:
            # relationship_statement = f"\t<http://purl.obolibrary.org/obo/{rel_id_list[0]}> :{term2} ;\n"
            relationship_statement = f"\t<http://purl.obolibrary.org/obo/{rel_id_list[0]}> :{term2}"
            for rel_id in rel_id_list[1:]:
                relationship_statement_seg = f"\t<http://purl.obolibrary.org/obo/{rel_id}> :{term2}"
                # relationship_statement = relationship_statement + ";\n" + "+" + relationship_statement_seg + ''
                relationship_statement = relationship_statement + " ;\n" + relationship_statement_seg + ""
        else:
            relationship_statement = f"\t<http://purl.obolibrary.org/obo/{rel_id_list[0]}> :{term2}"

        # relationship_statement = relationship_statement + " \n\n"
        return (relationship_statement, rel_id_list)
    else:
        return ("", [])


def import_tables():
    """
    Import AOP Wiki tables from the aop_wiki_tables_directory
    :return(3 dataframes): returns dataframes of the EC_table, KE_table, KER_table
    """
    # Import AOP EC table data
    os.chdir("/Users/mmandal/Library/CloudStorage/OneDrive-ResearchTriangleInstitute/projects/NCATS_AOP")
    AOP_EC_table = pd.read_csv("aop_wiki_tables/aop_ke_ec.csv")
    AOP_KE_table = pd.read_csv("aop_wiki_tables/aop_ke_mie_ao.tsv", sep="\t")
    AOP_KER_table = pd.read_csv("aop_wiki_tables/aop_ke_ker.tsv", sep="\t")

    # Convert KE, AOP, Evennt, and relationshihp columns to integers
    AOP_EC_table["KE"] = [int(re.sub(r"Event\:", "", x)) for x in AOP_EC_table["Key Event"]]
    AOP_EC_table['AOP'] = [int(re.sub(r"Aop\:", "", x)) for x in AOP_EC_table["AOP"]]

    AOP_KER_table['AOP'] = [int(re.sub(r"Aop\:", "", x)) for x in AOP_KER_table["AOP"]]
    AOP_KER_table["Event1"] = [int(re.sub(r"Event\:", "", x)) for x in AOP_KER_table["Event1"]]
    AOP_KER_table["Event2"] = [int(re.sub(r"Event\:", "", x)) for x in AOP_KER_table["Event2"]]
    AOP_KER_table["Relationship"] = [int(re.sub(r"Relationship\:", "", x)) for x in AOP_KER_table["Relationship"]]

    AOP_KE_table["KE"] = [int(re.sub(r"Event\:", "", x)) for x in AOP_KE_table["Key Event"]]
    AOP_KE_table['AOP'] = [int(re.sub(r"Aop\:", "", x)) for x in AOP_KE_table["AOP"]]

    return AOP_EC_table, AOP_KE_table, AOP_KER_table


def create_EC_dict(AOP_num, AOP_EC_table):
    """
    Takes an AOP number and the EC table and returns a filtered EC table and
    a dictionary of all of the KEs in the AOP
    :param AOP_num (int): AOP number to use for filtering
    :param AOP_EC_table: Full EC table from AOP Wiki
    :return(DF, dictionary): dictionary of KE terms for the inputted AOP
        AOP table filtered for the inputted AOP
    """
    AOP_EC_filtered = AOP_EC_table[AOP_EC_table["AOP"] == AOP_num].copy()
    EC_dict = {}
    for index, row in AOP_EC_filtered.iterrows():
        row_dict = dict(row)
        if row["KE"] not in EC_dict.keys():
            EC_dict[row["KE"]] = [row_dict]
        else:
            EC_dict[row["KE"]].append(row_dict)
    return EC_dict, AOP_EC_filtered


def create_AO_dict(AOP_num, AOP_KE_table):
    """
        Takes an AOP number and the KE table and returns
        a dictionary of all of the Adverse Outcomes (AOs) in the AOP
        :param AOP_num (int): AOP number to use for filtering
        :param AOP_EC_table: Full KE table from AOP Wiki
        :return(DF, dictionary): dictionary of KE terms for the inputted AOP
            AOP table filtered for the inputted AOP
    """
    AOP_KE_filtered = AOP_KE_table[AOP_KE_table["AOP"] == AOP_num].copy()
    AO_dict = {}
    for index, row in AOP_KE_filtered.iterrows():
        AO_dict[row.KE] = re.sub(r",", ";", row["Adverse Outcome"])
    return AO_dict


def create_ke_dicts(AOP_num, AOP_KER_table):
    """
    Tales an AOP number and the Key Event Relationships and returns a list
        of the KE pairs (the KEs adjacent to each other in the AOP), a list
        of the order the KEs are in the AOP, a dictionary to look up which
        KE follows the KE of interest.
    :param AOP_num: AOP number to be processed
    :param AOP_KER_table: Key Event Relationship table. Dataframe containing
        information on the order of KEs in an AOP
    :return (list of tuples, dict, list of integers): a list of the KE pairs
        (the KEs adjacent to each other in the AOP), a list of the order the
        KEs are in the AOP, a dictionary to look up which KE follows the
        KE of interest.
    """
    AOP_KER_filtered = AOP_KER_table[AOP_KER_table["AOP"] == AOP_num].reset_index().copy()
    KE_pairs = []
    KE_order_dict = {}
    KE_order = []
    for index, row in AOP_KER_filtered.iterrows():
        if row.adjacent != "adjacent":
            continue
        if index == 0:
            KE_order.append(row.Event1)
            KE_order.append(row.Event2)
        else:
            KE_order.append(row.Event2)

        KE_order_dict[row.Event1] = row.Event2
        KE_pairs += [(row.Event1, row.Event2)]
    return KE_pairs, KE_order_dict, KE_order


def create_ttl_dicts(AOP_EC_filtered):
    """
    Takes the EC table filtered for the AOP being processed and
        returns 4 dicts of all of the class, individual,
        relationship, and object statements for the ttl file
    :param AOP_EC_filtered(DF): EC table filtered for the AOP being processed
    :return(4 dicts):  dictionaries containing statements for
        the ttl file.
    """

    ### Create ttl dicts
    classes = {}
    individuals = {}
    relationships = {}
    object_statements = {}

    # Cycle through rows and create classes and individuals
    for index, row in AOP_EC_filtered.iterrows():
        row = row.rename(lambda x: re.sub(r"[\s\/]", "_", x.lower()))
        # if object_id is not already in classes.keys() add object_id

        # if row.object_id not in classes.keys() and row.object_id is not NA
        if not pd.isna(row.object_id):
            class_statement, individuals_statement = process_term(row.object_id, row.object_term, row.object_source)
            classes[row.object_id] = class_statement
            individuals[row.object_id] = individuals_statement
        # if process_phenotype_id is not already in individuals.keys() add process_phenotype_id

        # if row.process_phenotype_id not in individuals.keys() and not pd.isna(row.process_phenotype_id):
        if not pd.isna(row.process_phenotype_id):
            class_statement, individuals_statement = process_term(row.process_phenotype_id, row.process_phenotype_term,
                                                                  row.process_phenotype_source)
            classes[row.process_phenotype_id] = class_statement
            individuals[row.process_phenotype_id] = individuals_statement

        row_relationship_statement, rel_id_list = get_relationship_statement(row.action, row.object_term,
                                                                             row.object_source, "Object", "",
                                                                             row.process_phenotype_term,
                                                                             row.process_phenotype_source,
                                                                             "Process/Phenotype")
        object_statements = get_object_statement(rel_id_list, object_statements)
        relationships[(row.object_id, row.process_phenotype_id)] = row_relationship_statement
        if row.ke in KE_order_dict.keys():
            try:
                next_KE_num = KE_order_dict[row.ke]
                EC_dict[next_KE_num]
            except:
                continue

            for next_KE in EC_dict[next_KE_num]:
                if row.process_phenotype_id is not np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                    row_relationship_statement, rel_id_list = get_relationship_statement(row.action,
                                                                                         row.process_phenotype_term,
                                                                                         row.process_phenotype_source,
                                                                                         "Process/Phenotype",
                                                                                         "",
                                                                                         next_KE[
                                                                                             "Process/Phenotype Term"],
                                                                                         next_KE[
                                                                                             "Process/Phenotype Source"],
                                                                                         "Process/Phenotype")
                    relationships[
                        (row.process_phenotype_id, next_KE["Process/Phenotype ID"])] = row_relationship_statement
                    object_statements = get_object_statement(rel_id_list, object_statements)
                elif row.process_phenotype_id is not np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                    row_relationship_statement, rel_id_list = get_relationship_statement(row.action,
                                                                                         row.process_phenotype_term,
                                                                                         row.process_phenotype_source,
                                                                                         "Process/Phenotype",
                                                                                         "",
                                                                                         next_KE["Object Term"],
                                                                                         next_KE["Object Source"],
                                                                                         "Object")
                    relationships[(row.process_phenotype_id, next_KE["Object ID"])] = row_relationship_statement
                    object_statements = get_object_statement(rel_id_list, object_statements)
                elif row.process_phenotype_id is np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                    row_relationship_statement, rel_id_list = get_relationship_statement(row.action,
                                                                                         row.object_term,
                                                                                         row.object_source,
                                                                                         "Object",
                                                                                         "",
                                                                                         next_KE[
                                                                                             "Process/Phenotype Term"],
                                                                                         next_KE[
                                                                                             "Process/Phenotype Source"],
                                                                                         "Process/Phenotype")
                    relationships[(row.object_id, next_KE["Process/Phenotype ID"])] = row_relationship_statement
                    object_statements = get_object_statement(rel_id_list, object_statements)
                elif row.process_phenotype_id is np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                    row_relationship_statement, rel_id_list = get_relationship_statement(row.action,
                                                                                         row.object_term,
                                                                                         row.object_source,
                                                                                         "Object",
                                                                                         "",
                                                                                         next_KE["Object Term"],
                                                                                         next_KE["Object Source"],
                                                                                         "Object")
                    relationships[(row.object_id, next_KE["Object ID"])] = row_relationship_statement
                    object_statements = get_object_statement(rel_id_list, object_statements)
    return classes, individuals, relationships, object_statements


def write_ttl(outfile, EC_dict, KE_order, KE_order_dict, classes, individuals, relationships,
              object_statements, IRI, title, status):
    '''
    Write ttl file using statements from the dictionaries created by create_ttl_dicts().
    :param outfile( (str): filt to write to
    :param EC_dict (dict): Dictionaries of event componemts
    :param KE_order (list): List of KEs in order of occurrence in the AOP
    :param KE_order_dict (dict): Dict of KEs that you can use to get the next KE in the sequence
    :param classes: Dict of class statements
    :param individuals: Dict of individual statements
    :param relationships: Dict of relationship statements
    :param object_statements: Dict of object statements
    :param IRI: IRI statement to be added to header
    :return: None, a .ttl file is written instead
    '''

    error_c = 0
    missing_components = []
    # write predetermined header
    header = \
    f'''@prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix : <http://www.co-ode.org/ontologies/ont.owl#> .
    @base <http://www.w3.org/2002/07/owl#> .

    {IRI}\n{title}\n{status}
        '''
    with open(outfile, "w+") as f:
        f.write(header)

    # Write pre-determined header for classes
    with open(outfile, "a") as f:
        f.write("\n\n#################################################################")
        f.write("\n#   Classes")
        f.write("\n#################################################################\n\n")

    # Loop through class statements and write them to the output file
    for c, s in classes.items():
        with open(outfile, "a") as f:
            f.write(s)

    # Write pre-determined header for individuals
    with open(outfile, "a") as f:
        f.write("\n\n#################################################################")
        f.write("\n#   Individuals")
        f.write("\n#################################################################\n\n")

    # Loop through KEs in order (using KE_order) and write an individuals statement for each KE
    with open(outfile, "a") as f:
        for KE_id in KE_order:
            # print(KE_id)
            try:
                EC_dict[KE_id]
            except:
                error_c += 1
                missing_components.append(KE_id)
                EC_dict[KE_id] = []

            for KE in EC_dict[KE_id]:
                if KE_id in KE_order_dict.keys():
                    next_KE_id = KE_order_dict[KE_id]
                    try:
                        next_KEs = EC_dict[next_KE_id]

                    except:
                        error_c += 1
                        missing_components.append(next_KE_id)
                        next_KEs = []
                else:
                    next_KEs = []

                if KE["Object ID"] is not np.nan:  # if there is an object, write an instance of that object
                    f.write(individuals[KE['Object ID']])

                if KE["Object ID"] is not np.nan and KE[
                    "Process/Phenotype ID"] is not np.nan:  # if there are both and object and process, write the relationshp
                    f.write(" ;\n" + relationships[(KE['Object ID'], KE["Process/Phenotype ID"])])
                    f.write(" .\n\n")

                if KE["Process/Phenotype ID"] is not np.nan:  # if there is a process, write an instance of that process
                    f.write(individuals[KE['Process/Phenotype ID']])

                # if KE_id in KE_order_dict.keys():  # if there is a next KE in the order_dict
                for next_KE in next_KEs:  # go through the next KEs
                    try:
                        if KE["Process/Phenotype ID"] is not np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                            # print(" ;\n" + relationships[KE["Process/Phenotype ID"], next_KE["Process/Phenotype ID"]])
                            f.write(" ;\n" + relationships[KE["Process/Phenotype ID"], next_KE["Process/Phenotype ID"]])
                        elif KE["Process/Phenotype ID"] is not np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                            f.write(" ;\n" + relationships[KE["Process/Phenotype ID"], next_KE["Object ID"]])
                        elif KE["Process/Phenotype ID"] is np.nan and next_KE["Process/Phenotype ID"] is not np.nan:
                            f.write(" ;\n" + relationships[KE["Object ID"], next_KE["Process/Phenotype ID"]])
                        elif KE["Process/Phenotype ID"] is np.nan and next_KE["Process/Phenotype ID"] is np.nan:
                            f.write(" ;\n" + relationships[KE["Object ID"], next_KE["Object ID"]])
                    except:
                        continue
                f.write(" .\n\n")

    # Write predetermined object header
    with open(outfile, "a") as f:
        f.write("\n\n#################################################################")
        f.write("\n#   Object Statements")
        f.write("\n#################################################################\n\n")

    # Loop through class statements and write them to the output file
    for o, s in object_statements.items():
        with open(outfile, "a") as f:
            f.write(s)
    if error_c > 0:
        aop_summary_txt = f"{AOP_num}: missing KE(s){list(set(missing_components))}\n"
    else:
        aop_summary_txt = f"{AOP_num}: complete\n"
    with open(log, 'a') as logf:
        logf.write(aop_summary_txt)
    return error_c


AOP_EC_table, AOP_KE_table, AOP_KER_table = import_tables()

AOP_nums = list(set(AOP_EC_table["AOP"]))
# AOP_nums = [100]
# AOP_nums = [202]
# AOP_nums = [23]
# AOP_nums = [102]
# AOP_nums = [429, 411, 412]
c_completed = []
c_missing = []
log = f"output/070323/log.txt"
open(log, "w+").close()

# Loop through the AOPs in AOP_nums and try to write a ttl file for each AOP. Keep a list of
#   successful and failed AOPs, Print the error message when an AOP fails.
for AOP_num in AOP_nums:
    # print(f"AOP {AOP_num}")
    outfile = f"output/070323/aop_{AOP_num}_model.ttl"

    try:
        # download DFs and create dicts
        EC_dict, AOP_EC_filtered = create_EC_dict(AOP_num, AOP_EC_table)
        AO_dict = create_AO_dict(AOP_num, AOP_KE_table)
        KE_pairs, KE_order_dict, KE_order = create_ke_dicts(AOP_num, AOP_KER_table)
        classes, instances, relationships, object_statements = create_ttl_dicts(AOP_EC_filtered)

        # Write ttl file
        AO = AOP_KE_table["Adverse Outcome"][AOP_num]
        IRI = f"<https://noctua.apps.renci.org/model/AOP_{AOP_num}> a owl:Ontology ."
        title = f'<https://noctua.apps.renci.org/model/AOP_{AOP_num}> <http://purl.org/dc/elements/1.1/title> "{AO}"^^xsd:string .'
        status = f'<https://noctua.apps.renci.org/model/{AOP_num}> <http://geneontology.org/lego/modelstate> "review"^^xsd:string .'
        error_c = write_ttl(outfile, EC_dict, KE_order, KE_order_dict, classes, instances, relationships,
                            object_statements, IRI, title, status)


    except Exception as e:
        # c_missing.append(AOP_num)
        with open(log, 'a') as logf:
            txt = traceback.format_exc()

            #  indent error message
            txt = re.sub(r"\n(\s*)?(?=[^$])", "\n\t", txt)
            txt = re.sub(r"^", "\t", txt)

            logf.write(f"{AOP_num} is missing elements\n{txt}")

            continue
    if error_c > 0:
        c_missing.append(AOP_num)
    else:
        c_completed.append(AOP_num)

with open(log, 'a') as logf:
    logf.write(f"\nResults:{len(c_completed)} complete, {len(c_missing)} have missing components")
print(f"Results:{len(c_completed)} are complete, {len(c_missing)} have missing elements")

# c_error: [1, 12, 13, 16, 17, 36, 37, 39, 40, 57, 58, 60, 61, 72, 78, 82, 86, 90, 97, 151, 186, 190, 191, 195, 202, 203, 204, 206, 209, 213, 214, 215, 216, 218, 219, 220, 230, 233, 235, 238, 241, 242, 245, 256, 257, 258, 264, 265, 266, 267, 268, 272, 273, 274, 275, 276, 277, 278, 280, 285, 286, 289, 290, 291, 292, 293, 294, 296, 297, 299, 300, 302, 303, 305, 306, 307, 309, 310, 311, 312, 318, 319, 320, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 335, 336, 337, 338, 340, 341, 343, 344, 345, 347, 348, 349, 358, 359, 361, 365, 366, 367, 374, 377, 379, 382, 383, 384, 385, 386, 387, 388, 389, 392, 394, 396, 398, 399, 406, 409, 410, 411, 412, 413, 422, 424, 425, 428, 429, 430]

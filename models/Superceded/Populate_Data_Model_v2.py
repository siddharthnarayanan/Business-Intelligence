#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import pandas as pd
from itertools import product
from difflib import SequenceMatcher as sm

## For POS-tagging and/or tokenization
import nltk
from nltk.corpus import stopwords

## For dependency parsing
import spacy
## Configure spaCy English-pretrained model
nlp = spacy.load('C:\\Users\\mallabi\\AppData\\Local\\Continuum\\anaconda3\\Lib\\site-packages\\en_core_web_sm\\en_core_web_sm-2.1.0')

# ## Testing to get time/day/money
# import duckling
# from datetime import datetime

## Initiate duckling-wrapper: takes few seconds to complete
# duck = duckling.DucklingWrapper()


# In[ ]:





# ### Helper Functions

# In[2]:


def checkATE(input_sent):
    """
    Check if it's ATE.
    """
    input_sent = [sent.lower() for sent in input_sent]
    ATE = 'ATE not found!'
    
    for ele in input_sent:
        if 'additional termination events' in ele:
            ATE = 'Additional Termination Event'
            return ATE
        else:
            continue
            
    return ATE


# In[3]:


########################################-----------------ERISA-----------------########################################
def checkEventType(input_sent):
    """
    Check what type of event it is.
    """
    
    input_sent = [sent.lower() for sent in input_sent]
    
    for ele in input_sent:
        if 'net asset value' in ele:       
            return 'net asset value'
        elif 'erisa' in ele:
            return 'erisa'
        elif 'key person' in ele:
            return 'Key Person'
        elif 'investment manager' in ele:
            return 'investment manager'        
        elif 'financials' in ele:
            return 'financials'
        elif 'other optional termination' in ele:
            return 'other optional early termination'
        elif 'regulatory authority' in ele:
            return 'regulatory authority'
        elif 'material change' in ele:
            return 'material change'
        
        else:
            continue
            
    return None


def checkElectiveTermination(input_sent):
    """
    
    """
    if type(input_sent) == list:
        input_sent = [sent.lower() for sent in input_sent]
        elective_termination = 'No indication found!'
        
        for sent in input_sent:
            if 'optional' in sent:
                elective_termination = 'Elective'
                return elective_termination
            else:
                continue
                
        return elective_termination
    
    
def getAffectedParty(input_sent):
    """
    
    """
    
    regex_party = '(Party)\s*[A-Z]'
    affected_party = 'Affected party not found!'
    
    for ele in input_sent:
        if 'Affected Party' in ele: 
            affected_party = re.search(regex_party, ele).group()
            affected_party = affected_party.split(' ')[1].upper()
            return affected_party
        else:
            continue
            
    return affected_party

    
def checkElectingParty(electing_party = None, affected_party = None):
    """
    
    """
    
    notification = False
    notified_parties = []
    
    if affected_party == 'B' and electing_party == 'A':
        notification = True
        notified_parties.append('A')
        notified_parties.append('B')
        return notification, notified_parties
    
    elif affected_party == 'B' and electing_party == 'B':
        return notification, notified_parties
    
    elif affected_party not in ['A', 'B'] or electing_party not in ['A', 'B']:
        notification = 'Indication not available!'
        notified_parties.append('Indication not available!')
        
        return notification, notified_parties
    

def checkAffectedParty(affected_party = None, event_type = None):
    """
    event_type = ['ERISA', 'NAV']
    
    """
    written_bases_determination_c1 = False
    written_bases_determination_c2 = False
    if affected_party == 'B':
        if event_type in ['ERISA', 'erisa']:
            written_bases_determination_c1 = True
            written_bases_determination_c2 = True            
            return (written_bases_determination_c1, written_bases_determination_c2)
        elif event_type == 'NAV':
            return (written_bases_determination_c1, written_bases_determination_c2)
        
    else:
        ## DON'T KNOW WHAT PATH TO FOLLOW AS IT'S NOT AVAILABLE IN DECISION-TREE
        return (written_bases_determination_c1, written_bases_determination_c2)
    
    
def prohibitedTransaction(affected_party = None, event_type = None):
    """
    
    """
    
    prohibited_transaction = 'Indication not available!'
    conditions = checkAffectedParty(affected_party = affected_party, event_type = event_type)
    if affected_party == 'B' and any(conditions) == True and event_type in ['ERISA', 'erisa']:    
        prohibited_transaction = True
        return prohibited_transaction
    else:
        return prohibited_transaction


def exemptTransaction(affected_party = None, event_type = None):
    """
    
    """
    exempt = False
    if prohibitedTransaction(affected_party = affected_party, event_type = event_type):
        return exempt
    else:
        exempt = 'Indication not available!'
        return exempt


# In[49]:


########################################-----------------NAV-----------------########################################
## Use above functions: checkElectiveTermination, checkElectingParty, checkAffectedParty

def getValuedParty(input_sent):
    """
    Valued Party
    """ 
    valued_party = None
    children = []
    doc = nlp(input_sent)
    for token in doc:
        if str(token) in ['of']:
            if str(token.head.text) == 'Value':
                children.extend([str(child) for child in token.children if len(child) == 1])
                valued_party = list(set(children))[0]
    
    return 'Party '+valued_party

            
def getChangeDirection(input_sent):
    """
    NAV_Trigger
    """
    
    doc = nlp(input_sent[0])
    change_directions = []
    for token in doc:
        if str(token) == 'Value':
            if str(token.head.pos_) == 'VERB':
                change_directions.append(token.head.text)
                
    NAV_Trigger = list((set(change_directions)))
    return NAV_Trigger



def getValuationAmount(input_sent):
    """
    
    """

    regex_p = '\d+\%'  ## To get PERCENT values
    regex_d = 'USD+[0-9].+\.'  ## To get DOLLAR amount

    result_p = re.findall(regex_p, input_sent, flags = re.IGNORECASE)
    result_d = re.findall(regex_d, input_sent, flags = re.IGNORECASE)
    
    non_below_valuation_amounts = []
    for i,j in enumerate(result_p):
        temp = 'valuation_amount_'+str(i)
        non_below_valuation_amounts.append((temp, j))

    below_valuation_amounts = []
    for i,j in enumerate(result_d):
        temp = 'valuation_amount_below_'+str(i)
        below_valuation_amounts.append((temp, j))
        
    if not non_below_valuation_amounts:
        non_below_valuation_amounts.append('Empty List. Values not found!')
    if not below_valuation_amounts:
        below_valuation_amounts.append('Empty List. Values not found!')
        
    
    return non_below_valuation_amounts, below_valuation_amounts


def getValuationDayMonth(input_sent):
    """
    
    """

    doc = nlp(input_sent[0].split(':')[1])
    valuation_days = []
    valuation_months = []

    for chunk in doc.noun_chunks:
        if str(chunk.root.text) == 'Day':
            valuation_days.append(chunk.text)
        elif str(chunk.root.text) == 'month':
            valuation_months.append(chunk.text)            

    return valuation_days, valuation_months


# In[5]:


#######################-----------------KeyPerson, InvestmentManager, Financials-----------------########################
def getMiniBranchFields(input_sent, mini_branches, eve_cat = None, elec_term = None, party_affected = None, ATE = None):
    """
    Function for small branches such as: Key-person, Investment Manager, Financials, Other Optional Early Termination, 
    Regulatory Authority, Material Change
    
    """
    
    branch_name = 'Not available in pre-defined phrases!'
        
    input_sent = input_sent.lower()    
    for branch in mini_branches:
        if branch in input_sent:
            branch_name = branch
            break
            
    branch_dict = {'Event Type': branch_name, 'Event Category': eve_cat, 'Type of Termination': elec_term, 
                   'Affected Party': party_affected, 'ATE': ATE}
    
    return branch_dict


# In[24]:


def getMajorBranchFields(ATE = None, eve_typ = None, elec_term = None, eve_cat = None, party_affected = None, 
                         party_elected = None, notif_req = None, notif_party = None, party_valued = None, nav = None, 
                         eqaul_more = None, below = None, written_clause_1 = None, written_clause_2 = None, 
                         prohibit_tran = None, exem_tran = None, event = None, value_days = None, value_months = None):
    """
    Function to make a fields:values dictionary for ERISA and NAV
    """
    
    
    if event == 'Net Asset Value' or event == 'net asset value':
    ## List of NAV-fields
        NAV_fields_dict = {'ATE': ATE, 'Event Type': eve_typ, 'Type of Termination': elec_term, 'Event_Category': eve_cat,
                         'Affected Party': party_affected, 'Electing Party': party_elected, 
                         'Notification Required': notif_req, 'Notified Party': notif_party, 
                         'Valued Party': party_valued, 'NAV_Trigger': nav, 'Equal or More': eqaul_more, 'Below': below, 
                          }
        
        return NAV_fields_dict

    elif event == 'ERISA' or event == 'erisa':
        ## List of ERISA-fields
        ERISA_fields_dict = {'ATE': ATE, 'Event Type': eve_typ, 'Type of Termination': elec_term, 'Event_Category': eve_cat,
                             'Affected Party': party_affected, 'Electing Party': party_elected, 
                             'Notification Required': notif_req, 'Notified Party': notif_party, 
                             'Written Basis Determination - 1': written_clause_1, 
                             'Written Basis Determination - 2': written_clause_2, 
                             'Prohibited Transaction': prohibit_tran, 'Exempt Transaction': exem_tran}    
        return ERISA_fields_dict
    
    else:
        return None


# In[ ]:





# ### Execution

# ### Input Data

# In[9]:


# ## Input data: Provide sentences as per order described in power-point and utilize decision-tree to creare logic
# ip_1 = ["Additional Termination Event. The following Additional Termination Events will apply:"]
# ip_2_3_6_23 = ["Optional Early Termination1. Both Party A and Party B shall have the right, as long as no \
#                Termination Event or Event of Default shall have occurred, and upon three (3) \
#                 Local Business Day's prior written notice to terminate any Transaction with immediate effect. "]
# ip_4 = ["Party B, in each such instance, shall be the sole Affected Party5"]
# ip_7_to_14 = ["Net Asset Value Decline4. On the last Local Business Day of any calendar month, the Net Asset Value of \
#               Party B, as reported in writing as a final Net Asset Value declines: (A) by forty percent (40%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the twelfth prior calendar month; \
#               or (B) by thirty percent (30%) or more compared to the Net Asset Value of Party B on the \
#               last Local Business Day of the third prior calendar month; or (C) by twenty percent (20%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the prior calendar month; \
#               or (D) as of any day the Net Asset Value of Party B declines below USD30,000,000."]

# ip_15_to_17_21_22_24 = [' Prohibited Transaction3. If either Party2 reasonably determines, and (1) notifies the other party in writing of such determination, and (2) promptly provides to the other \
# Party (in writing , if promptly requested by the other Party) the basis for the determination, that this Agreement or any Transaction contemplated hereby constitutes or is \
# likely to constitute a "prohibited transaction" under ERISA (as defined in Part 5) and/or the Code (as defined in Part 5) and that no exemption from the "prohibited \
# transaction" provisions of ERISA and the Code is available with respect to this Agreement and/or such Transaction. Such Additional Termination Event shall be deemed to \
# have occurred when the condition of clause (1) has been satisfied, if clause (2) is eventually satisfied. If the required basis is provided to the other Party in accordance with \
# clause (2) along with the initial notification, the Additional Termination Event occurs at the time of the initial notification.']

# ip_19 = ["Key Person4. XXX ceases to be responsible for the day-to-day portfolio management of Party B and a successor reasonably acceptable to Party A is not appointed within a reasonable time thereafter "]
# ip_20 = ["Investment Manager4. ABC ceases to act at any time as investment manager on behalf of Party B in the same or similar capacity as on the date of this Agreement."]
# ip_21 = [ "Financials4. Party B shall fail to deliver (i) any financial information pursuant to Part 3(b)(i) of this Schedule within five (5) calendar days of Party A's notice to Party B of Party B's failure to provide such information, or (ii) any financial statements or financial information pursuant to Party 3(b)(ii) of this Schedule within two (2) calendar days of Party A's notice to Party B of Party B's failure to provide such information"]
# ip_24 = ["Regulatory Authority4. The Regulator's authorisation of Party B or approval is withdrawn or subjected to conditions that would have a material adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement."]
# ip_25 = ["Material Change4. Any of the constitutive documents or the Prospectus relating to Party B (in the case of the Prospectus) from time to time are materially amended or modified in a manner which would have a material, adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement or any Transaction hereunder."]


# ### With whole ATE-data: Identify paragraphs in all ATE-text and return appropriate fields to be populated in data model

# In[7]:


def getData():
    """
    
    """

    with open('ATE_raw_text.txt', 'r') as ate:
        all_ATE = ate.read()

    ## Making two lists of same text data: If I keep raw text in original form then it's easy to catch langauge dependencies with spaCy
    all_ATE_elements_original = re.split('\n{2} \n{2}', all_ATE)
    all_ATE_elements = [ele.lower() for ele in all_ATE_elements_original]
    
    return all_ATE_elements_original, all_ATE_elements


def searchParagraph(keyword, all_elements):
    """
    Use key-words and/or phrases to look for a relevant sentence/paragraph in the ATE-text (all_elements). ATE-text is split 
    into list of paragraphs for this process.
    """
    matched_elements = []
    for ele in all_elements:
        if keyword in ele.lower():
            matched_elements.append(ele)
        
    return matched_elements


def dictValuesToList(input_dict):
    """
    Convert all values of a dictionary into list.
    """
    
    for i,j in input_dict.items():
        if type(j) == list:
            pass
        elif type(j) == str:
            j = [j]
            input_dict[i] = j
        elif type(j) == bool:
            j = [j]
            input_dict[i] = j
#         elif j is None:
#             j = ['None']
        else:
            continue
        
    return input_dict


def convertDictToDf(input_dict):
    """
    Convert dictionary to dataframe when values of dictionary are lists of varying lengths.
    """
    
    input_dict = dictValuesToList(input_dict)
    
    flat = [[(k, v) for v in vs] for k, vs in input_dict.items()]
    df_ls = [dict(items) for items in product(*flat)]
    
    return pd.DataFrame(df_ls)

def getGlobalFields(ATE = 'None', party_affected = 'None', elec_term = 'None'):
    """
    Pre-defined set of fields to return if input-clause is same as one of the global statements.
    """
    global_var_dict = {}
    global_var_dict['ATE'] = ATE
    global_var_dict['Affected_Party'] = party_affected
    global_var_dict['Elective Termination'] = elec_term
    
    return global_var_dict


def checkSimilarity(input_clause, global_sents):
    """
    
    """
    sim = 0
    match = None
    threshold = 0.90

    for ind, sent in enumerate(global_sents):
        sim_temp = sm(None, sent, input_clause).ratio()
        if sim_temp > sim and sim_temp >= threshold:
            sim = sim_temp
            match = sent
            return ind
        else:
            continue
            
    return False


# ## Example-0 (Take user-input and get relevant o/p)

# In[19]:


## Only NAV
ip_test = ["Net Asset Value Decline4. On the last Local Business Day of any calendar month, the Net Asset Value of               Party B, as reported in writing as a final Net Asset Value declines: (A) by forty percent (40%) or more               compared to the Net Asset Value of Party B on the last Local Business Day of the twelfth prior calendar month;               or (B) by thirty percent (30%) or more compared to the Net Asset Value of Party B on the               last Local Business Day of the third prior calendar month; or (C) by twenty percent (20%) or more               compared to the Net Asset Value of Party B on the last Local Business Day of the prior calendar month;               or (D) as of any day the Net Asset Value of Party B declines below USD30,000,000. "]

# ## Only ERISA
ip_test = [' Prohibited Transaction3. If either Party2 reasonably determines, and (1) notifies the other party in writing of such determination, and (2) promptly provides to the other Party (in writing , if promptly requested by the other Party) the basis for the determination, that this Agreement or any Transaction contemplated hereby constitutes or is likely to constitute a "prohibited transaction" under ERISA (as defined in Part 5) and/or the Code (as defined in Part 5) and that no exemption from the "prohibited transaction" provisions of ERISA and the Code is available with respect to this Agreement and/or such Transaction. Such Additional Termination Event shall be deemed to have occurred when the condition of clause (1) has been satisfied, if clause (2) is eventually satisfied. If the required basis is provided to the other Party in accordance with clause (2) along with the initial notification, the Additional Termination Event occurs at the time of the initial notification.']

# # ## For others
# ip_test = ["Investment Manager4. ABC ceases to act at any time as investment manager on behalf of Party B in the same or similar capacity as on the date of this Agreement."]
# ip_test = [ "Financials4. Party B shall fail to deliver (i) any financial information pursuant to Part 3(b)(i) of this Schedule within five (5) calendar days of Party A's notice to Party B of Party B's failure to provide such information, or (ii) any financial statements or financial information pursuant to Party 3(b)(ii) of this Schedule within two (2) calendar days of Party A's notice to Party B of Party B's failure to provide such information"]
# ip_test = ["Regulatory Authority4. The Regulator's authorisation of Party B or approval is withdrawn or subjected to conditions that would have a material adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement."]
# ip_test = ["Material Change4. Any of the constitutive documents or the Prospectus relating to Party B (in the case of the Prospectus) from time to time are materially amended or modified in a manner which would have a material, adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement or any Transaction hereunder."]


# In[ ]:





# In[53]:


def execute(input_clause):
    """
    
    """

    ## Possible input phrases
    phrases = ['additional termination event', 'erisa', 'net asset value', 'investment manager', 'financials', 
               'material change', 'regulatory authority', 'other optional termination']


    ## Extract information from GLOBAL STATEMENTS
    global_statements = ["Additional Termination Event. The following Additional Termination Events will apply:", 
                         "Party B, in each such instance, shall be the sole Affected Party5", 
                         "Optional Early Termination1. Both Party A and Party B shall have the right, as long as no \
                             Termination Event or Event of Default shall have occurred, and upon three (3) \
                             Local Business Day's printor written notice to terminate any Transaction with immediate effect. "]
    
    ate_statement = [global_statements[0]]
    ate_input_keyword = phrases[0]
    matched_elements = searchParagraph(ate_input_keyword, ate_statement)
    ATE = checkATE(matched_elements)

    affected_party_statement = [global_statements[1]]
    affected_party = getAffectedParty(affected_party_statement)    

    termination_statement = [global_statements[2]]
    EVENT_CATEGORY = 'termination'
    matched_elements = searchParagraph(EVENT_CATEGORY, termination_statement)
    elective_termination = checkElectiveTermination(matched_elements)

    ## Check if input_clause is similar to one of the global statements.
    value = checkSimilarity(input_clause, global_statements)
    
    if value is not False:
        if ATE in global_statements[value]:
            global_dict = getGlobalFields(ATE = ATE)
            global_dict_df = convertDictToDf(global_dict)    
            return global_dict_df
        elif 'Affected Party' in global_statements[value]:
            global_dict = getGlobalFields(party_affected = affected_party)
            global_dict_df = convertDictToDf(global_dict)    
            return global_dict_df
        elif 'Termination' in global_statements[value]:
            global_dict = getGlobalFields(elec_term = elective_termination)
            global_dict_df = convertDictToDf(global_dict)    
            return global_dict_df
        else:
            return 'False Alarm!'
                
    else:
    
        ## Get event-type
        event_type = checkEventType(input_clause)

        ## For Net Asset Value
        if  event_type in phrases and event_type == 'net asset value':
            print ('Done-1', event_type)

            NAV_Trigger = getChangeDirection(input_clause)
            non_below, below = getValuationAmount(input_clause[0])   
            valuation_days, valuation_months = getValuationDayMonth(input_clause)
            valuation_info_non_below = []
            for n,d,m in zip(non_below, valuation_days, valuation_months):
                n = n + (d,) + (m,)
                valuation_info_non_below.append(n)
            
            print ('Done-2')

            if len(ip_test) > 1:
                matched_elements = ' '.join(matched_elements)     
                matched_elements = re.sub(pattern = '(\\n)', string = matched_elements, repl = '')
                valued_party = getValuedParty(input_sent = matched_elements)
            else:
                valued_party = getValuedParty(input_sent = input_clause[0])

            print ('Done-3')

            electing_party = 'A'
            notification_required, notified_party = checkElectingParty(affected_party = affected_party, electing_party = electing_party)
            print ('Done-4')

            major_branch = getMajorBranchFields(ATE = ATE, eve_typ = event_type, elec_term = elective_termination, 
                                                eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
                                                party_elected = electing_party, notif_req = notification_required, 
                                                notif_party = notified_party, party_valued = valued_party, nav = NAV_Trigger, 
                                                eqaul_more = valuation_info_non_below, below = below, 
                                                written_clause_1 = None, written_clause_2 = None, prohibit_tran = None, 
                                                exem_tran = None, event = event_type)

            major_branch_df = convertDictToDf(major_branch)

            
            ## Split columns as per excel-data-model: order of following lines matter!
            major_branch_df['Valuation Month'] = list(map(lambda ele: ele[3], major_branch_df['Equal or More']))
            major_branch_df['Valuation Day'] = list(map(lambda ele: ele[2], major_branch_df['Equal or More']))
            major_branch_df['Equal or More'] = list(map(lambda ele: ele[1], major_branch_df['Equal or More']))
            major_branch_df['Below'] = list(map(lambda ele: ele[1], major_branch_df['Below']))
            
            return major_branch_df
        
        ## For ERISA
        elif event_type in phrases and event_type == 'erisa':

            print ('Done-1')

            electing_party = 'A'
            notification_required, notified_party = checkElectingParty(affected_party = affected_party, electing_party = electing_party)
            written_bases_determination_c1, written_bases_determination_c2 = checkAffectedParty(affected_party = affected_party, 
                                                                                                        event_type = event_type)
            print ('Done-2')

            prohibited_transact = prohibitedTransaction(affected_party = affected_party, event_type = event_type)
            exempt_transact = exemptTransaction(affected_party = affected_party, event_type = event_type)

            major_branch = getMajorBranchFields(ATE = ATE, eve_typ = event_type, elec_term = elective_termination, 
                                                eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
                                                party_elected = electing_party, notif_req = notification_required, 
                                                notif_party = notified_party, party_valued = None, nav = None, 
                                                eqaul_more = None, below = None, written_clause_1 = written_bases_determination_c1, 
                                                written_clause_2 = written_bases_determination_c1, 
                                                prohibit_tran = prohibited_transact, exem_tran = exempt_transact, 
                                                event = event_type)

            major_branch_df = convertDictToDf(major_branch)

            return major_branch_df

        ## For mini-branches    
        elif event_type in phrases and event_type not in ['erisa', 'net asset value']:
            input_matched_elements = searchParagraph(event_type, input_clause)
            input_matched_elements = ' '.join(input_matched_elements)

            print ('Done-1')

            mini_branch = getMiniBranchFields(input_sent = input_matched_elements, mini_branches = phrases, 
                                              eve_cat = EVENT_CATEGORY, elec_term = elective_termination, 
                                              party_affected = affected_party, ATE = ATE)

            mini_branch_df = convertDictToDf(mini_branch)  

            return mini_branch_df

        else:
            message = 'Event_type not found in pre-defined phrases/keywords!'
            print(message)
            return pd.DataFrame()


# In[ ]:





# ### Example-1 (w/ ERISA and NAV)

# In[9]:


# def execute(input_keyword):
#     """
    
#     """
#     all_ATE_elements_original, all_ATE_elements = getData()
   

#     ## Possible input phrases
#     phrases = ['additional termination event', 'erisa', 'net asset value', 'investment manager', 'financials', 
#                'material change', 'regulatory authority', 'other optional termination']

#     ate_input_keyword = phrases[0]
#     matched_elements = searchParagraph(ate_input_keyword, all_ATE_elements)
#     ATE = checkATE(matched_elements)


#     ## Try for ERISA: Need to automate what sentences to take as input!
#     if input_keyword == 'erisa' and input_keyword in phrases:
#         matched_elements = searchParagraph(input_keyword, all_ATE_elements)
#         event_type = checkEventType(matched_elements)

#         print ('Done-1')

#         EVENT_CATEGORY = 'termination'
#         default_keyword = EVENT_CATEGORY
#         matched_elements = searchParagraph(default_keyword, all_ATE_elements)
#         elective_termination = checkElectiveTermination(matched_elements)

#         print ('Done-2')

#         default_keyword = 'affected party'
#         matched_elements = searchParagraph(default_keyword, all_ATE_elements)
#         affected_party = getAffectedParty(matched_elements)

#         electing_party = 'A'
#         notification_required, notified_party = checkElectingParty(affected_party = affected_party, electing_party = electing_party)
#         written_bases_determination_c1, written_bases_determination_c2 = checkAffectedParty(affected_party = affected_party, 
#                                                                                                     event_type = event_type)

#         print ('Done-3')

#         prohibited_transact = prohibitedTransaction(affected_party = affected_party, event_type = event_type)
#         exempt_transact = exemptTransaction(affected_party = affected_party, event_type = event_type)


#         major_branch = getMajorBranchFields(ATE = ATE, eve_typ = event_type, elec_term = elective_termination, 
#                                             eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
#                                             party_elected = electing_party, notif_req = notification_required, 
#                                             notif_party = notified_party, party_valued = None, nav = None, 
#                                             eqaul_more = None, below = None, written_clause_1 = written_bases_determination_c1, 
#                                             written_clause_2 = written_bases_determination_c1, 
#                                             prohibit_tran = prohibited_transact, exem_tran = exempt_transact, 
#                                             event = input_keyword)

        
#         major_branch_df = convertDictToDf(major_branch)
    
#         return major_branch_df
    
        
#     elif input_keyword == 'net asset value' and input_keyword in phrases:
#         matched_elements = searchParagraph(input_keyword, all_ATE_elements_original)
#         event_type = checkEventType(matched_elements)
#         print ('Done-1')
        
#         NAV_Trigger = getChangeDirection(matched_elements)
#         non_below, below = getValuationAmount(matched_elements[0])   
#         print ('Done-2')
        
#         if len(matched_elements) > 1:
#             matched_elements = ' '.join(matched_elements)     
#             matched_elements = re.sub(pattern = '(\\n)', string = matched_elements, repl = '')
#             valued_party = getValuedParty(input_sent = matched_elements)

#         default_keyword = 'affected party'
#         matched_elements = searchParagraph(default_keyword, all_ATE_elements_original)
#         affected_party = getAffectedParty(matched_elements)    
#         print ('Done-3')
        
#         EVENT_CATEGORY = 'termination'
#         default_keyword = EVENT_CATEGORY
#         matched_elements = searchParagraph(default_keyword, all_ATE_elements)
#         elective_termination = checkElectiveTermination(matched_elements)
#         print ('Done-4')
        
#         electing_party = 'A'
#         notification_required, notified_party = checkElectingParty(affected_party = affected_party, electing_party = electing_party)
#         print ('Done-5')
        
#         major_branch = getMajorBranchFields(ATE = ATE, eve_typ = event_type, elec_term = elective_termination, 
#                                             eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
#                                             party_elected = electing_party, notif_req = notification_required, 
#                                             notif_party = notified_party, party_valued = valued_party, nav = NAV_Trigger, 
#                                             eqaul_more = non_below, below = below, written_clause_1 = None, 
#                                             written_clause_2 = None, prohibit_tran = None, exem_tran = None, 
#                                             event = input_keyword)
        
#         major_branch_df = convertDictToDf(major_branch)
    
#         return major_branch_df
    
#     elif input_keyword in phrases and input_keyword not in ['erisa', 'net asset value']:
#         input_matched_elements = searchParagraph(input_keyword, all_ATE_elements)
#         input_matched_elements = ' '.join(input_matched_elements)
        
#         default_keyword = 'affected party'
#         matched_elements = searchParagraph(default_keyword, all_ATE_elements_original)
#         affected_party = getAffectedParty(matched_elements)    
#         print ('Done-1')
        
#         EVENT_CATEGORY = 'termination'
#         default_keyword = EVENT_CATEGORY
#         matched_elements = searchParagraph(default_keyword, all_ATE_elements)
#         elective_termination = checkElectiveTermination(matched_elements)
#         print ('Done-2')
            
#         mini_branch = getMiniBranchFields(input_sent = input_matched_elements, mini_branches = phrases, 
#                                           eve_cat = default_keyword, elec_term = elective_termination, 
#                                           party_affected = affected_party)
        
#         mini_branch_df = convertDictToDf(mini_branch)
        
#         return mini_branch_df
    
#     else:
#         return "Something's wrong!"
        


# In[ ]:





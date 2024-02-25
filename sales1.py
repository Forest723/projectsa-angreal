import pandas as pd
import os
import requests
import json
import atexit
from openai import OpenAI
from dotenv import load_dotenv
from agency_swarm import set_openai_key, Agency, Agent
from agency_swarm.tools import Retrieval, CodeInterpreter
from agency_swarm.agents.browsing import BrowsingAgent
from agency_swarm.agents.coding import CodingAgent

# load keys here
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
data_gov_api_key = os.getenv("DATA_GOV_API_KEY")
if not data_gov_api_key:
    raise ValueError("DATA_GOV_API_KEY not found in environment variables")
client = OpenAI(api_key=api_key) 
set_openai_key(api_key)

# data filtering and pulling and cleaning could use a ton of work im sure
# New build_query function
def cayg_build_query(base_url, version, entity, select=None, top=None, states=None, federal_share_not_zero=False):
    query = f"{base_url}/{version}/{entity}"
    params = []
    if select:
        select_query = ','.join(select)
        params.append(f"$select={select_query}")
    if top:
        params.append(f"$top={top}")
    filter_conditions = []
    if states:
        states_query = " or ".join([f"stateCode eq '{state}'" for state in states])
        filter_conditions.append(f"({states_query})")
    if federal_share_not_zero:
        filter_conditions.append("(federalShareObligated gt 0 or federalShareObligated lt 0)")
    if filter_conditions:
        filter_query = " and ".join(filter_conditions)
        params.append(f"$filter={filter_query}")
    if params:
        query += "?" + "&".join(params)
    return query

def cayg_call_api(api_endpoint, max_records=200):
    all_data = []
    top = 100
    skip = 0
    while True:
        paginated_url = f"{api_endpoint}&$top={top}&$skip={skip}"
        response = requests.get(paginated_url)
        if response.status_code == 200:
            print("API call successful.")
            data = response.json()['PublicAssistanceApplicantsProgramDeliveries']
            all_data.extend(data)
            if len(data) < top:
                break
            skip += top
            if skip >= max_records:
                break
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break
    return {'PublicAssistanceApplicantsProgramDeliveries': all_data}

# Existing parse_data function
def cayg_parse_data(data):
    print("Parsing data.")
    relevant_data = data['PublicAssistanceApplicantsProgramDeliveries']
    df = pd.DataFrame(relevant_data)
    return df

cayg_selected_fields = ["declarationType", "stateCode", "disasterNumber", "incidentType", "applicantName", "federalShareObligated"]
cayg_states_of_interest = ['CA']

cayg_query_url = cayg_build_query(
    base_url="https://www.fema.gov/api/open",
    version="v1",
    entity="PublicAssistanceApplicantsProgramDeliveries",
    select=cayg_selected_fields,
    top=100,
    states=cayg_states_of_interest,
    federal_share_not_zero=True
)

def cayg_save_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)
    print(f"Data saved to '{file_path}'")
try:
    cayg_json_file_path = "c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/cayg/processed_pa_data.json"
    if not os.path.exists(cayg_json_file_path):
        raw_data = cayg_call_api(cayg_query_url)
        processed_data = cayg_parse_data(raw_data)
        processed_data_dict = processed_data.to_dict(orient='records')
        cayg_save_json(processed_data_dict, cayg_json_file_path)
    else:
        print(f"JSON file already exists at '{cayg_json_file_path}'. Skipping file creation.")
except Exception as e:
    print(f"Error occurred: {e}")

# New build_query function
def hm_build_query(base_url, version, entity, select=None, top=None, states=None, federal_share_not_zero=False):
    query = f"{base_url}/{version}/{entity}"
    params = []
    if select:
        select_query = ','.join(select)
        params.append(f"$select={select_query}")
    if top:
        params.append(f"$top={top}")
    filter_conditions = []
    if states:
        states_query = " or ".join([f"state eq '{state}'" for state in states])
        filter_conditions.append(f"({states_query})")
    if federal_share_not_zero:
        filter_conditions.append("(federalShareObligated gt 0 or federalShareObligated lt 0)")
    if filter_conditions:
        filter_query = " and ".join(filter_conditions)
        params.append(f"$filter={filter_query}")
    if params:
        query += "?" + "&".join(params)
    return query

def hm_call_api(api_endpoint, max_records=200):
    all_data = []
    top = 100
    skip = 0
    while True:
        paginated_url = f"{api_endpoint}&$top={top}&$skip={skip}"
        response = requests.get(paginated_url)
        if response.status_code == 200:
            print("API call successful.")
            data = response.json()['HazardMitigationAssistanceProjects']
            all_data.extend(data)
            if len(data) < top:
                break
            skip += top
            if skip >= max_records:
                break
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break
    return {'HazardMitigationAssistanceProjects': all_data}

# Existing parse_data function
def hm_parse_data(data):
    print("Parsing data.")
    relevant_data = data['HazardMitigationAssistanceProjects']
    df = pd.DataFrame(relevant_data)
    return df

hm_selected_fields = ["programArea", "programFy","state", "disasterNumber", "recipient", "federalShareObligated"]
hm_states_of_interest = ['California']

hm_query_url = hm_build_query(
    base_url="https://www.fema.gov/api/open",
    version="v3",
    entity="HazardMitigationAssistanceProjects",
    select=hm_selected_fields,
    top=100,
    states=hm_states_of_interest,
    federal_share_not_zero=True
)

def hm_save_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)
    print(f"Data saved to '{file_path}'")
try:
    hm_json_file_path = "c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/hma/processed_hm_data.json"

    if not os.path.exists(hm_json_file_path):
        raw_data = hm_call_api(hm_query_url)
        processed_data = hm_parse_data(raw_data)
        processed_data_dict = processed_data.to_dict(orient='records')
        hm_save_json(processed_data_dict, hm_json_file_path)
    else:
        print(f"JSON file already exists at '{hm_json_file_path}'. Skipping file creation.")
except Exception as e:
    print(f"Error occurred: {e}")

# New build_query function
def preparedness_build_query(base_url, version, entity, select=None, top=None, states=None):
    query = f"{base_url}/{version}/{entity}"
    params = []
    if select:
        select_query = ','.join(select)
        params.append(f"$select={select_query}")
    if top:
        params.append(f"$top={top}")
    filter_conditions = []
    if states:
        states_query = " or ".join([f"state eq '{state}'" for state in states])
        filter_conditions.append(f"({states_query})")
    if filter_conditions:
        filter_query = " and ".join(filter_conditions)
        params.append(f"$filter={filter_query}")
    if params:
        query += "?" + "&".join(params)
    return query

def preparedness_call_api(api_endpoint, max_records=200):
    all_data = []
    top = 100
    skip = 0
    while True:
        paginated_url = f"{api_endpoint}&$top={top}&$skip={skip}"
        response = requests.get(paginated_url)
        if response.status_code == 200:
            print("API call successful.")
            data = response.json()['EmergencyManagementPerformanceGrants']
            all_data.extend(data)
            if len(data) < top:
                break
            skip += top
            if skip >= max_records:
                break
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break
    return {'EmergencyManagementPerformanceGrants': all_data}

# Existing parse_data function
def preparedness_parse_data(data):
    print("Parsing data.")
    relevant_data = data['EmergencyManagementPerformanceGrants']
    df = pd.DataFrame(relevant_data)
    return df

preparedness_selected_fields = ["state", "legalAgencyName", "projectEndDate", "fundingAmount"]
preparedness_states_of_interest = ['California']

preparedness_query_url = preparedness_build_query(
    base_url="https://www.fema.gov/api/open",
    version="v2",
    entity="EmergencyManagementPerformanceGrants",
    select=preparedness_selected_fields,
    top=100,
    states=preparedness_states_of_interest
)

def preparedness_save_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)
    print(f"Data saved to '{file_path}'")

try:
    preparedness_json_file_path = 'c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/preparedness/processed_preparedness_data.json'
    if not os.path.exists(preparedness_json_file_path):
        raw_data = preparedness_call_api(preparedness_query_url)
        processed_data = preparedness_parse_data(raw_data)
        processed_data_dict = processed_data.to_dict(orient='records')
        preparedness_save_json(processed_data_dict, preparedness_json_file_path)
    else:
        print(f"JSON file already exists at '{preparedness_json_file_path}'. Skipping file creation.")
except Exception as e:
    print(f"Error occurred: {e}")

#idea for top agents
agency_coordinator = Agent(
    name="Agency Coordinator",
    description="Communicates with the user to both facilitate conversation and utilize the agency to build sales intelligence and help with opportunity management.",
    instructions='''
    The coordinator's main focus should be to help the user leverage the agency for any sales related queries. This would include the following:
    - Identify potential leads based on the insights gained from data associated to particular products or services through the following agents:
        1.) Close As You Go Analyst
        2.) Hazard Mitigation Analyst
        3.) Preparedness Analyst
    - Craft a robust strategy for pursuing a lead while highlight both how the product or service can be of use and any sales tips
    - Work with the outreach team to create tailored outreach messages and templates for communications
    - Build out or edit leads and current work in the pipeline through the pipeline management agent
    - If a user needs contact information, clarify if they are looking for internal connections or information from the state contact list and utilize your training data to provide results
    - If the user is looking for request for proposal (RFP) insights, clarify if they are looking for specific opportunities or how to access opportunities for the relevant lead and utilize your training data to provide results
    - If the user has identified a RFP they want to pursue, leverage the deal_calculator and any other relevant agents to determine if it meets the criteria
    
    There is no particular order with which the coordinator should work but rather leverage any of the agents at any point to help the user with whatever query they have    
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/strategy",
    tools=[Retrieval] #I could use an entire breakdown of services here...
)

# AI Agents with Adjusted Roles and Capabilities
cayg_analyst = Agent(
    name="CAYG Analyst",
    description="Focused on helping provide data-driven insights to help sell Close As You Go (CAYG) to those in need of a grants management software as a service.",
    instructions='''
    - Conduct an in-depth analysis of openFEMA datasets to identify leads, focusing on the highest amounts of federalShareObligated. 
    - Based on how the user asks about leads (specific or broad), adjust the returns by either providing either a singular lead's details or a small list of leads (always be succinct yet comprehensive while including key data points). 
    - Utilize the insights gained paired with Close As You Go knowledge to help return information to the coordinator.
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/cayg",
    tools=[Retrieval]
)

hma_analyst = Agent(
    name="Hazard Mitigation Assistance Analyst",
    description="Focused on helping provide data-driven insights to help sell Hazard Mitigation Assistance Services to those in need of a grants management software as a service.",
    instructions='''
    - Conduct an in-depth analysis of openFEMA datasets to identify leads, focusing on the highest amounts of federalShareObligated. 
    - Based on how the user asks about leads (specific or broad), adjust the returns by either providing either a singular lead's details or a small list of leads (always be succinct yet comprehensive while including key data points). 
    - Utilize the insights gained paired with Hazard Mitigation Services knowledge to help return information to the coordinator.
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/hma",
    tools=[Retrieval]
)

preparedness_analyst = Agent(
    name="Emergency Management Preparedness Analyst",
    description="Focused on helping provide data-driven insights to help sell Emergency Management Preparedness Grant Services to those in need of a grants management software as a service.",
    instructions='''
    - Conduct an in-depth analysis of openFEMA datasets to identify leads, focusing on the highest amounts of projectAmount. 
    - Based on how the user asks about leads (specific or broad), adjust the returns by either providing either a singular lead's details or a small list of leads (always be succinct yet comprehensive while including key data points). 
    - Utilize the insights gained paired with Hazard Mitigation Services knowledge to help return information to the coordinator.
        - The EMPG is to support a comprehensive, all-hazard emergency preparedness system by building and sustaining the core capabilities contained in the NPG's. Examples include:
            - Completing the Threat and Hazard Identification and Risk Assessment (THIRA) process.
            - Strengthening a state or community's emergency management governance structure.
            - Updating and approving specific emergency plans.
            - Designing and conducting exercises that enable whole community stakeholders to examine and validate core capabilities and the plans needed to deliver them to the targets identified through the THIRA.
            - Targeting training and verifying identified capabilities.
            - Initiating or achieving a whole community approach to security and emergency management.
            - Strengthening cybersecurity measures.
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/preparedness",
    tools=[Retrieval]
)

#Agnogstic Team
outreach_engagement = Agent(
    name="Outreach and Engagement Specialist",
    description="Works with identified leads to highlight the strategy for selling the either the product, the service, or both.",
    instructions='''
    - Review information provided to understand each lead's details.
    - Develop personalized outreach messages in a professional format for each lead, highlighting how the product or service can address the lead's unique challenges.
    - When needing additional information (like specific sector challenges, news about the lead's organization, etc.), provide detailed queries to the Browsing Agent to assist in customizing outreach or gathering relevant information.
    ''',
    files_folder=None,
    tools=None
)

pipeline_manager = Agent( #this bloke really needs some help
    name="Pipeline Manager",
    description="Helps take an identified lead and vet if it aligns with any of the clients in the pipeline.",
    instructions='''
    - Analyze incoming leads to check for potential matches within our client pipelines.
    - For each lead, cross-reference with existing pipeline data to identify any connections or opportunities.
    - If a match is found, gather relevant details and inform the stakeholder about the lead's position and potential next steps in the pipeline.
    - In cases where no immediate match is found, propose strategies for expanding the pipeline or leveraging other resources to accommodate the new lead.
    - Upon confirming a lead's relevance, coordinate with the data management agent to update the pipeline records. This includes modifying the existing data or adding new information using the `json.dumps` method, ensuring all updates are saved to the designated file in the specified directory.
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/pipeline",
    tools=[Retrieval]
)

contact_identifier = Agent(
    name="Contact Identifier",
    description="Identifies contacts to reach out to when pursuing a lead.",
    instructions='''
    - When the user is requesting a potential lead's point of contact, utilize your training set to provide either offering a state official or an internal contact.
    - As a last resort, you should provide step-by-step instructions to find contacts, specifically looking for the head of community development.
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/contact_information",
    tools=[Retrieval]
)

rfp_identifier = Agent(
    name="Request for Proposal Identifier",
    description="Identifies a potential RFP that is relevant to what the identified lead needs and what the relevant product or service provides.",
    instructions='''
    - When the user is requesting to learn more about what RFPs may be associated to the identified lead, either provide RFPs or how to access them by leveraging your training set.
    - As a last resort, you should provide step-by-step instructions so that so that the browsing agent knows how to efficiently browse and return data.
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/requests_for_proposal",
    tools=[Retrieval]
)

deal_calculator = Agent(
    name="Deal Calculator",
    description="This agent's responsibility is to intake an identified rfp and run it through a team of agents to determine if it is worthy of pursuit.",
    instructions='''
    Pass on the following questions to the agents and request a score to apply to the applicable quesiton
    1. scope alignment - work with the deal_strategy agent
    2. contract value - work with the contract evaluator
    3. internal matches - work with the internal staff alignment
    4. quals check - work with the quals agent
    5. deal overview - work with the deal overview agent

    prompt the relevant agents to intake ALL scores from the agents. there should be 5 in total
    to get the score, you multiple the weight of the answer by the % assigned to the question. 
    you then add up the scores and then divde that by 5 (or if you take each of the % * 5 and add up it equals 5)
    - < 69% probably shouldnt bid unless there is a good reason
    - 70-80% proceed with caution
    - 80%+ send it

    Local weights per question
        1. .12
        2. .15
        3. .38
        4. .12
        5. .23
    State weights per question
        1. .13
        2. .2
        3. .32
        4. .15
        5. .2
    Federal weights per question
        1. .13
        2. .2
        3. .32
        4. .15
        5. .2

    You should be capable of utilizing your codeinterpreter tool to calculate the final score and based on findings, provide a report on the final verdict!
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/rfp_bank",
    tools=[CodeInterpreter, Retrieval] # put the RFP in here if its a go. the agency should be able to tell you i think based on search methods.
)

deal_strategy = Agent(
    name="Strategy Analysis and Alignment",
    description="This agent's responsibility is to intake the rfp's scope of work assign a score based on how well it aligns with the provided products and services.",
    instructions='''
    - 1. analyze rfp, pull scope to see if it aligns with the stragegy and services outlined in the training set. Based on findings, provide a score.
        strategy, methodology, and training align with the scope (score=5)
        missing methodology or training? (score=3)
        missing strategy? (score=1)
        missing strategy, methodology, and training? (score=0)
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/strategy",
    tools=[Retrieval]
)

contract_evaluator = Agent(
    name="Contract Value Evaluator",
    description="This agent's responsibility is to work with the rfp_itentifier to place a value on the contract. Based on the value, assign a score.",
    instructions='''
    - 2. utilize the rfp_identifier to retrieve the pull the contract value and lifetime (if possible). based on findings, assign a score based on the value. 
        $10M+ (score=5)
        $5M - $10M (score=3)
        $1M - $5M (score=1)
        <$1M (score=0)
    ''',
    files_folder=None, 
    tools=[Retrieval]
)

internal_staff_allignment = Agent(
    name="Internal Staff Alignment",
    description="This agent's responsibility is to intake the needs for services and pair with the relevant staff and leadership. Based on the analysis, assign as score to gauge the ability to deliver.",
    instructions='''
    - 3. pair location and need with relevant internal contacts with a correlated strength of relationship
        The state is in our alignment, we have strong relationships in the area, have competent staff available and local, and a partner to assign (score=5)
        The state is a mid-tier priority, we have a decent relationship in the area, can fill some staffing roles in a hybrid sense, and a partner in mind (score=3)
        The state isn't a priority but we have some staff available and possibly a partner (score=1)
        The state is not a priority, we don't have the staff, and we don't have a partner (score=0)
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/internal_staff", # staffing docs for availability, delivery risk, partners
    tools=[Retrieval]
)

quals_agent = Agent(
    name="Qual Checker",
    description="This agent's responsibility is to intake information about the RFP's scope and try to match it with the qualifications stored in training set.",
    instructions='''
    - 4. pair quals training set with quals in RFP and score
        quals are there (score=5)
        some of the quals are there (score=3)
        the quals arent there (score=0)
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/qualifications", # mock quals 
    tools=[Retrieval]
)

overview_evaluation = Agent(
    name="Deal Overview",
    description="This agent's responsibility is to look at the overall scores gathered so far and assign one more score before final evaluation.",
    instructions='''
    - 5. evaluate the current state of the staffing, quals, and contract value then determine if there is an incumbent. based on these two insights, assign a score.
        staff, quals, and value are all there and incumbency is in our favor (score=5)
        part of staff, quals, and value is missing and the incumbency is in question (score=3)
        the staff, quals, and value isn't there and the incumbency isn't in our favor (score=0)
    ''',
    files_folder=None,
    tools=[Retrieval]
)

# ideas...
# we need to bridge the gap with Deloitte. current work, timelines, and contacts could be incredibly valuable as insights for end users

browsing_agent = BrowsingAgent()
browsing_agent.instructions = "\n\nPlease browse the web and execute actions based on the instructions given by the other agents. If you are getting stuck, please stop and return what you've gathered to the rfp identifier."

coding_agent = CodingAgent()
coding_agent.instructions += "\n\nExecute code as you are instructed to."

# Define Manifesto
agency_manifesto = """
Manifesto:
- The sales team's mission is to revolutionize public sector grant management by leveraging innovative technology and data-driven insights.
- The sales team's goal is to help the user identify a lead, pursue the lead in an ethical way, and provide helpful services to the leads.
- The sales team's functions include the following:
    - Analyze FEMA and Govwin data to identify opportunities, contracts, and contacts paired with other insights to determine if a deal is worthy of pursuit.
    - Provide a tailored strategy for pursit.
    - Craft an approacah that utilzied specially crafted communications messages. 
"""

# Instantiate the Agency with Updated Hierarchy
agency_chart = [
    agency_coordinator,
    [agency_coordinator, cayg_analyst], # key: cayg_analyst reports to agency_coordinator
    [agency_coordinator, hma_analyst],
    [agency_coordinator, preparedness_analyst],
    [agency_coordinator, outreach_engagement],
    [agency_coordinator, contact_identifier],
    [agency_coordinator, rfp_identifier],
    [agency_coordinator, deal_calculator],
    [deal_calculator, rfp_identifier],
    [deal_calculator, deal_strategy],
    [deal_calculator, contract_evaluator],
    [contract_evaluator, rfp_identifier],
    [deal_calculator, contact_identifier],
    [deal_calculator, internal_staff_allignment],
    [internal_staff_allignment, contact_identifier],
    [deal_calculator, quals_agent],
    [deal_calculator, overview_evaluation]
]

# Initialize your agents and agency outside of the main function
agency = Agency(agency_chart, shared_instructions=agency_manifesto)

# file cleanup
def cleanup_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):  # Check if the file is a JSON file
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)  # Delete the file
                print(f"Deleted JSON file: {file_path}")
            except Exception as e:
                print(f"Failed to delete JSON file: {file_path}. Reason: {e}")

directory_to_cleanup_cayg = "c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/cayg"
directory_to_cleanup_hma = "c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/hma"
directory_to_cleanup_preparedness = "c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/preparedness"
atexit.register(cleanup_json_files, directory_to_cleanup_cayg)
atexit.register(cleanup_json_files, directory_to_cleanup_hma)
atexit.register(cleanup_json_files, directory_to_cleanup_preparedness)

#demo!
agency.demo_gradio(height=600)
import pandas as pd
import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from agency_swarm import set_openai_key, Agency, Agent
from agency_swarm.tools import Retrieval
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

#data filtering and pulling and cleaning could use a ton of work im sure
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

def cayg_call_api(api_endpoint, max_records=1000):
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
cayg_states_of_interest = ['NC', 'SC', 'TX', 'NY', 'CA', 'MS', 'AL', 'LA', 'VA', 'MD', 'CO', 'OR', 'WA', 'NJ', 'HI', 'AL', 'PR'] #steve's list

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
    cayg_json_file_path = 'c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/cayg/processed_pa_data.json'

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

def hm_call_api(api_endpoint, max_records=1000):
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
hm_states_of_interest = ['North Carolina', 'South Carolina', 'Texas', 'New York', 'California']

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
    hm_json_file_path = 'c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/hma/processed_hm_data.json'

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

def preparedness_call_api(api_endpoint, max_records=1000):
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
preparedness_states_of_interest = ['North Carolina', 'South Carolina', 'Texas', 'New York', 'California']

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
    description="Soley communicates with the user to both facilitate conversation and utilize the agency to identify leads, draft communications, and obtain other necessary details to help sales strategy.",
    instructions='''
    The coordinator's job is to oversee the entire sales process through the following actions:
    - Begin by asking the user which of the following parts of the agency they would like to work with:
        1.) CAYG Analyst
        2.) Hazard Mitigation Analyst
        3.) Preparedness
    - Once the user has identified which asset or service they are looking to sell, utilize the relevant analyst to identify potential leads based on the user's query.
    - Utilize the relevant analyst's knowledge alongside outreach engagement to craft a tailored strategy of pursuit based on the product or service identified alongside a professional outreach message (usually email). 
    - If a user needs contact information of an identified lead, pass information off to the contact identifier who will instruct the browsing agent on how to obtain the relevant information.
    - If the user is curious about any RFPs the identified lead may have, utilize the rpf identifier who will instruct the browsing agent on how to obtain the relevant information.
    - Check to see if there is anything currently in the pipline with the lead by working with the pipeline manager. 
        - When the pipeline manager is going to use the coding agent to update the pipeline json file, please support them with the relevant details needed based on what the rest of the agency has provided you for the leads. please fill in the rest yourself to your best ability or put 'Data Unavailable' and proceed.
    - If there is an opportunity to pair the services your analysts are knowledgable on together, please suggest ideas.
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
            - Completing the Threat and Hazard Identification and Risk Assessment (THIRA)process.
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
    - Review information provided by the Research Analyst to understand each lead's details.
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
    - Intake the lead from the relevant lead and verify if there is data aligning with the lead in the pipeline.
    - If there is aligning data, provide info to the user based on the current state of the pipeline.
    - If there is not data aligned, suggest a buildout of the pipeline using other agents. 
    - When a lead is identified please have the coding agent access a file called located at x and add or update data gathered from the previous agents to the file through json.dumps method
    import json
    # Example JSON data structure
    data = {
        "clients": []
    }
    def add_client(data, client_info):
        data['clients'].append(client_info)
    def update_client(data, client_id, updates):
        for client in data['clients']:
            if client['ID'] == client_id:
                client.update(updates)
                break
    # Example usage
    new_client = {
        "Client": "Potential, Existing, or Current Client",
        "Client POC Name": "Contact Identifier/Browsing Agent",
        "Client POC Email": "Contact Identifier/Browsing Agent",
        "Sub-Sector": "Dataset",
        "State": "Dataset",
        "Advantaged Client Segment": "Internal thing",
        "State Agency or County": "Dataset",
        "Operational Budget": "Budget Identifier/Browsing Agent",
        "RFP Status": "RFP Identifier - Lance",
        "RFP Site": "https://RFP Identifier.Lance.com",
        "Contract Name": "data.gov or something else or internals",
        "Account": "data.gov or something else or internal",
        "Service Description": "data.gov or something else or internal",
        "Contract Amount": "$data.gov or something else or internal",
        "Contract Expiration Date": "data.gov or something else or internal",
        "Internal POC": "Internal",
        "Incumbent": false,
        "ID": "00001",
        "General Notes": "MAY NEED TO GET BROKEN UP Notes on strategy, potential purusit ideas, inference from the data, market intelligence, and competitors"
      }
    add_client(data, new_client)
    update_client(data, "unique_id_123", {"State": "New State", "RFP Status": "closed"})
    # Convert data to JSON string to save or print
    json_data = json.dumps(data, indent=2)
    print(json_data) 
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/pipeline",
    tools=[Retrieval]
)

contact_identifier = Agent(
    name="Contact Identifier",
    description="Identifies contacts to reach out to when pursuing a lead.",
    instructions='''
    When the user is requesting a potential lead's point of contact, utilize the browsing agent to perform research and locate a relevant authoritative individual's name and email address so that the team can pursue the leads.
    ''',
    files_folder=None,
    tools=[Retrieval]
)

rfp_identifier = Agent(
    name="Request for Proposal Identifier",
    description="Identifies a potential RFP that is relevant to what the identified lead needs and what the relevant product or service provides.",
    instructions='''
    - When the user is requesting to learn more about what RFPs the identified lead may have recently issued, leverage the list of RFP sites in your training set alongside what you know about the identified lead to instruct the browsing agent to obtain specific details on RFP opportunitites.
    ''',
    files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/rfp_site_list",
    tools=[Retrieval]
)

#state_example = Agent(
    #name="x",
    #description="Identifies a potential RFP that is relevant to what the identified lead needs and what the relevant product or service provides.",
    #instructions='''
    #- When the user is requesting to learn more about what RFPs the identified lead may have recently issued, leverage the list of RFP sites in your training set alongside what you know about the identified lead to instruct the browsing agent to obtain specific details on RFP opportunitites.
   # ''',
  #  files_folder="c:/Users/Fcoon/Desktop/AI/Assistant/salesdocs/rfp_site_list",
 #   tools=[Retrieval]
#)

browsing_agent = BrowsingAgent()
browsing_agent.instructions = "\n\nPlease browse the web and execute actions based on the queries set by the other agents."

coding_agent = CodingAgent()
coding_agent.instructions += "\n\nExecute code as you are instructed to."

# Define Manifesto
agency_manifesto = """
Manifesto:
- The sales team's mission is to revolutionize public sector grant management by leveraging innovative technology and data-driven insights.
- The sales team's goal is to help the user identify a lead, pursue the lead in an ethical way, and provide helpful grants management services to the leads.
"""

# Instantiate the Agency with Updated Hierarchy
agency_chart = [
    agency_coordinator,
    [agency_coordinator, cayg_analyst],
    [agency_coordinator, hma_analyst],
    [agency_coordinator, preparedness_analyst],
    [agency_coordinator, outreach_engagement],
    [agency_coordinator, contact_identifier],
    [agency_coordinator, rfp_identifier],
    [agency_coordinator, pipeline_manager],
    [agency_coordinator, browsing_agent],
    [contact_identifier, browsing_agent],
    [rfp_identifier, browsing_agent],
    [pipeline_manager, coding_agent]
]

# Initialize your agents and agency outside of the main function
agency = Agency(agency_chart, shared_instructions=agency_manifesto)

agency.demo_gradio(height=600)
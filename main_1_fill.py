import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from EMInfraAPI.EMInfraImporter import EMInfraImporter
from EMInfraAPI.RequestHandler import RequestHandler
from EMInfraAPI.RequesterFactory import RequesterFactory
from EMInfraAPI.ResourceEnum import ResourceEnum
from EMInfraAPI.SettingsManager import SettingsManager
from ORM.Classes import Agent, Omgeving, AgentOmgeving
from ORM.Base import Base

if __name__ == '__main__':
    os.unlink('agents_all.db')
    engine = create_engine('sqlite:///agents_all.db', echo=True)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        omgeving_count = len(session.query(Omgeving).all())
        if omgeving_count == 0:
            session.add(Omgeving(naam="prd"))
            session.add(Omgeving(naam="tei"))
            session.add(Omgeving(naam="dev"))
            session.add(Omgeving(naam="aim"))
            session.commit()

        prd = session.query(Omgeving).filter(Omgeving.naam == "prd").one()
        tei = session.query(Omgeving).filter(Omgeving.naam == "tei").one()
        dev = session.query(Omgeving).filter(Omgeving.naam == "dev").one()
        aim = session.query(Omgeving).filter(Omgeving.naam == "aim").one()
        alle_omgevingen_dict = {'prd': prd, 'tei': tei, 'dev': dev, 'aim': aim}

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    settings_manager = SettingsManager(
        settings_path='/home/davidlinux/Documents/AWV/resources/settings_AwvinfraPostGISSyncer.json')

    importers = set()
    for env in alle_omgevingen_dict.keys():
        importers.add(EMInfraImporter(RequestHandler(RequesterFactory.create_requester(
            settings=settings_manager.settings, auth_type='JWT', env=env))))

    with Session(engine) as session:
        for importer in importers:
            omgeving = alle_omgevingen_dict[importer.request_handler.requester.environment]

            for a in importer.get_objects_from_oslo_search_endpoint_with_iterator(resource=ResourceEnum.agents):
                print(a)
                naam = a['purl:Agent.naam']
                ovo_code = a.get('tz:Agent.ovoCode', None)
                name_count = len(session.query(Agent).filter(Agent.naam == naam).all())
                if name_count == 0:
                    agent = Agent(naam=naam, void=a['tz:Agent.voId'])
                    session.add(agent)
                    session.commit()
                agent_in_db = session.query(Agent).filter(Agent.naam == naam).one()
                agent_omgeving = session.query(AgentOmgeving).filter(
                    AgentOmgeving.agent_id == agent_in_db.id, AgentOmgeving.omgeving_id == omgeving.id).all()
                print('agent_omgeving:')
                print(agent_omgeving)
                if len(agent_omgeving) == 0:
                    uuid = a['@id'][39:75]
                    print(uuid)
                    agent_omgeving = AgentOmgeving(agent_id=agent_in_db.id, omgeving_id=omgeving.id, uuid=uuid,
                                                   ovo_code=ovo_code)
                    session.add(agent_omgeving)
                    session.commit()

    with engine.connect() as conn:
        result = conn.execute(text("select agents.naam, agents_omgevingen.uuid, omgevingen.naam from agents "
                                   "left join agents_omgevingen on agents.id = agents_omgevingen.agent_id "
                                   "left join omgevingen on agents_omgevingen.omgeving_id = omgevingen.id"))
    print(result.all())



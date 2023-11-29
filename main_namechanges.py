import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from EMInfraAPI.EMInfraImporter import EMInfraImporter
from EMInfraAPI.RequestHandler import RequestHandler
from EMInfraAPI.RequesterFactory import RequesterFactory
from EMInfraAPI.ResourceEnum import ResourceEnum
from EMInfraAPI.SettingsManager import SettingsManager
from ORM.Classes import Agent, Omgeving, AgentOmgeving
from ORM.Base import Base

if __name__ == '__main__':
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

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    environment = prd.naam

    settings_manager = SettingsManager(
        settings_path='/home/davidlinux/Documents/AWV/resources/settings_AwvinfraPostGISSyncer.json')

    requester = RequesterFactory.create_requester(settings=settings_manager.settings, auth_type='JWT', env=environment,
                                                  multiprocessing_safe=True)
    request_handler = RequestHandler(requester)
    eminfra_importer = EMInfraImporter(request_handler)

    name_changes = [
        ("Agentschap Wegen en Verkeer", "Agentschap Wegen en Verkeer", "OVO000098"),

        ("AWV_EW_AN", "Afdeling Wegen en Verkeer Antwerpen", "OVO000548"),
        ("AWV_112_PUURS", "District Puurs", "OVO039695"),
        ("AWV_114_GEEL", "District Geel", "OVO039698"), # TODO
        ("AWV_121_ANTW", "District Antwerpen", "OVO039716"), # TODO
        ("AWV_123_BRECHT", "District Brecht", "OVO029060"),
        ("AWV_125_VOSSELAAR", "District Vosselaar", "OVO039727"), # TODO

        ("AWV_EW_VB", "Afdeling Wegen en Verkeer Vlaams-Brabant", "OVO000551"),
        ("AWV_211_HALLE", "District Halle", "OVO036851"),
        ("AWV_212_VILVOORDE", "District Vilvoorde", "OVO036849"), # TODO
        ("AWV_213_LEUVEN", "District Leuven", "OVO036847"),
        ("AWV_214_AARSCHOT", "District Aarschot", "OVO036850"),

        ("AWV_EW_WV", "Afdeling Wegen en Verkeer West-Vlaanderen", "OVO000552"),
        ("AWV_311_BRUGGE", "District Brugge", "OVO028757"),
        ("AWV_312_KORTRIJK", "District Kortrijk", "OVO028759"),
        ("AWV_313_IEPER", "District Ieper", "OVO028758"),
        ("AWV_315_OOSTENDE", "District Oostende", "OVO028760"),
        ("AWV_316_PITTEM", "District Pittem", "OVO028761"),

        ("AWV_EW_OV", "Afdeling Wegen en Verkeer Oost-Vlaanderen", "OVO000550"),
        ("AWV_411_GENT", "District Gent", "OVO039811"), # TODO
        ("AWV_412_OUDENAARDE", "District Oudenaarde", "OVO039815"),
        ("AWV_413_EEKLO", "District Eeklo", None),
        ("AWV_414_SINT-NIKLAAS", "District Sint-Niklaas", "OVO039821"),
        ("AWV_415_AALST", "District Aalst", "OVO039824"),

        ("AWV_EW_LB", "Afdeling Wegen en Verkeer Limburg", "OVO000549"),
        ("AWV_717_WEST-LIMBURG", "District West-Limburg", "OVO039787"),
        ("AWV_718_OOST-LIMBURG", "District Oost-Limburg", "OVO039784"),
        ("AWV_719_ZUID-LIMBURG", "District Zuid-Limburg", "OVO039780"),
        ("AWV_720_CENTRUM", "District Centraal Limburg", "OVO039775")
    ]

    with Session(engine) as session:
        for name_change in name_changes:
            try:
                agent = session.query(Agent).filter(Agent.naam == name_change[0]).one()
                agent.alias = agent.naam
                agent.naam = name_change[1]
                # agent.ovo_code = name_change[2]
            except NoResultFound:
                pass

        session.commit()

    with engine.connect() as conn:
        result = conn.execute(text("select agents.naam, agents_omgevingen.uuid, omgevingen.naam from agents "
                                   "left join agents_omgevingen on agents.id = agents_omgevingen.agent_id "
                                   "left join omgevingen on agents_omgevingen.omgeving_id = omgevingen.id"))
    print(result.all())



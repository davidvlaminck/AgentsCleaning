from typing import Optional, List

from sqlalchemy import Column, Integer, String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ORM.Base import Base


class Agent(Base):
    __tablename__ = 'agents'
    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column()
    void: Mapped[Optional[str]] = mapped_column()
    alias: Mapped[Optional[str]] = mapped_column()

    agent_omgevingen: Mapped[Optional[List["AgentOmgeving"]]] = relationship(back_populates="agent")

    def __repr__(self) -> str:
        return f'Agent(id={self.id!r}, name={self.naam!r}, ovo_code={self.ovo_code!r})'


class Omgeving(Base):
    tablename__ = 'omgevingen'
    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column()

    agent_omgevingen: Mapped[Optional[List["AgentOmgeving"]]] = relationship(back_populates="omgeving")

    def __repr__(self) -> str:
        return f'Omgeving(id={self.id!r}, name={self.naam!r})'


class AgentOmgeving(Base):
    __tablename__ = 'agents_omgevingen'
    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id = mapped_column(ForeignKey("agents.id"))
    omgeving_id = mapped_column(ForeignKey("omgevingen.id"))
    uuid: Mapped[str] = mapped_column()
    ovo_code: Mapped[Optional[str]] = mapped_column()

    agent: Mapped[Agent] = relationship(back_populates="agent_omgevingen")
    omgeving: Mapped[Omgeving] = relationship(back_populates="agent_omgevingen")

    def __repr__(self) -> str:
        return f'AgentOmgeving(agent_id={self.agent_id!r}, omgeving_id={self.omgeving_id!r}, uuid={self.uuid!r})'

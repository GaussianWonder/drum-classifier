from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from models import Base

"""
Every SoundFileModel should have at least one LabelModel associated with it.
This is what powers the training process.

Labels do not get dynamically created or deleted in the lifespan of a model which is training.
New labels do however appear depending on the folder structure of the assets directory,
    between training sessions of new models.

EG:
/assets
    /kick
        /edm
            /eg1.wav
        /techno
            /eg2.wav
    /percussion
        /eg3.wav

eg1.wav has
    Most Significant Label: kick
    Least Significant Label: edm
    Other Labels: _ (every other label extractable from the path, not applicable in this case)

eg2.wav has
    Most Significant Label: kick
    Least Significant Label: techno
    Other Labels: _ (every other label extractable from the path)

eg3.wav has
    Most Significant Label: percussion
    Least Significant Label: _
    Other Labels: _
"""


sound_file_association = Table(
    "labels_of_sound_files",
    Base.metadata,
    Column("label_id", ForeignKey("labels.id"), primary_key=True),
    Column("sound_file_id", ForeignKey("sound_files.id"), primary_key=True),
)


class LabelModel(Base):
    __tablename__ = "labels"

    # Identifier
    id = Column(Integer, primary_key=True)
    # Label identifier
    name = Column(String(260))

    msl_for = relationship("SoundFileModel", back_populates="msl")
    lsl_for = relationship("SoundFileModel", back_populates="lsl")
    l_for = relationship("SoundFileModel", secondary=sound_file_association, back_populates="labels")

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"LabelModel(" \
               f"name={self.name!r})"

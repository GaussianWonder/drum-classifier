from sqlalchemy.orm import relationship

from files import SoundFile
from sqlalchemy import Column, Integer, String, Float, ForeignKey

from models import Base
from models.label import sound_file_association

"""
The SoundFileModel is an unloaded SoundFile. Managed with SqlAlchemy ORM.
It is mappable to the SoundFile class, which can be used to perform algorithms on.
This intermediate step helps with caching, memory issues, and async processing.
"""


class SoundFileModel(Base):
    __tablename__ = "sound_files"

    # Identifier
    id = Column(Integer, primary_key=True)
    # File identifier
    path = Column(String(260))
    # File content identifier
    md5 = Column(String(255))
    sha1 = Column(String(255))
    sha256 = Column(String(255))

    msl_id = Column(Integer, ForeignKey("labels.id"))
    msl = relationship("LabelModel", back_populates="msl_for")

    lsl_id = Column(Integer, ForeignKey("labels.id"))
    lsl = relationship("LabelModel", back_populates="lsl_for")

    labels = relationship("LabelModel", secondary=sound_file_association, back_populates="l_for")

    # Computed details
    duration = Column(Float(precision=32, decimal_return_scale=None))

    def __init__(self, file: SoundFile):
        self.path = file.path

        identity = file.identity()
        self.md5 = identity.md5
        self.sha1 = identity.sha1
        self.sha256 = identity.sha256

        self.duration = file.duration

    def __repr__(self):
        return f"SoundFileModel(" \
               f"id={self.id!r}," \
               f"path={self.path!r}," \
               f"md5={self.md5!r}," \
               f"sha1={self.sha1!r}," \
               f"sha256={self.sha256!r}," \
               f"msl_id={self.msl_id!r}," \
               f"lsl_id={self.lsl_id!r}," \
               f"duration={self.duration!r})"

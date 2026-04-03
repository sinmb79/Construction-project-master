from __future__ import annotations

from enum import Enum


class ProjectDomain(str, Enum):
    건축 = "건축"
    토목_도로 = "토목_도로"
    토목_상하수도 = "토목_상하수도"
    토목_하천 = "토목_하천"
    조경 = "조경"
    복합 = "복합"

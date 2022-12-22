from pydantic import BaseModel


class ChannelModel(BaseModel):
    channel_id: int
    link: str
    tg_id: int
    btn_link_text: str = ''
    btn_link_url: str = ''


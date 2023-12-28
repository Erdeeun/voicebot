
####기본 정보 입력 ####
import streamlit as st
#openAI 패키지 추가
import openai

#audiorecorder 패키지 추가
from audiorecorder import audiorecorder

#파일 삭제를 위한 패키지 추가
import os

#시간 정보를 위한 패키지 추가
from datetime import datetime

#TTS패키지 추가
from gtts import gTTS

#음원파일 재생을 위한 패키지
import base64

#############################
### 기능 구현 함수 ########
def STT(audio):
  #파일 저장
  filename='input.mp3'
  audio.export(filename, format='mp3')
  #음원 파일 열기
  audio_file=open(filename, 'rb')
  #Whisper 모델을 활용해 텍스트 얻기
  transcript = openai.Audio.transcribe('whisper-1', audio_file)
  audio_file.close()
  #파일 삭제
  os.remove(filename)
  return transcript['text']

def ask_gpt(prompt, model):
  response = openai.ChatCompletion.create(model=model, messages=prompt)
  system_message = response['choices'][0]['message']
  return system_message['content']

def TTS(response):
  #gTTS를 활용하여 음성 파일 생성
  filename = 'output.mp3'
  tts = gTTS(text=response, lang='ko')
  tts.save(filename)

  #음원 파일 자동 재생
  with open(filename, 'rb') as f:
    data = f.read()
    b64 = base64.b64encode(data).decode()
    md = f'''
        <audio autoplay = 'True'>
        <source src = 'data:audio/mp3;base64,{b64}' type='audio/mp3'>
        </audio>
        '''
    st.markdown(md,unsafe_allow_html=True)
  #파일삭제
  os.remove(filename)


### 메인 함수 ####
def main():
  #기본 설정
  st.set_page_config(
    page_title = '음성 비서 프로그램',
    layout = 'wide'
  )

  #######################################
  ##2. 상태를 저장하기 위한 session_state 추가
  ##2-1 session_state 초기화
  ##2-2 리셋 코드
  ######################################
  #2-1 session_state 초기화
  if 'chat' not in st.session_state:
    st.session_state['chat'] = []

  if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role': 'system', 'content':'You are a thoughtful assistant. Respond to all in put in 25 word and answer in Korean'}]

  if 'check_reset' not in st.session_state:
    st.session_state['check_reset'] = False
######################################################

  #제목
  st.header('음성 비서 프로그램')

  #구분선
  st.markdown('--------------')

  #기본 설명
  with st.expander('음성 비서 프로그램에 관하여', expanded=True):
    st.write(
      '''
      - 음성 비서 프로그램의 UL는 스트림릿을 활용했다.
      - STT(Speach-To-Text)는 openAI의 Whisper AI를 활용했다.
      '''
    )

#####################################################################
#사이드바 설명
  with st.sidebar:
    #openai api_key 입력
    openai.api_key = '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'
    
    #= st.text_input(label = 'OPENAPI API 키', placeholder = 'Enter Your API Key', value='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',
     #                             type = 'password')


    st.markdown('------------------')


    #GPT모델을 선택하기 위한 라디오 버튼 생성
    model = st.radio(label='GPT 모델', options=['gpt-4', 'gpt-3.5-turbo'], index=1)
    #radio버튼은 무조건 앞에 단추가 선택되어서 index를 1로 (index는 0부터 시작)하면 2번째 항목 선택이 기본값

    st.markdown('-----------------')

    #리셋 버튼 생성
    if st.button(label='초기화'):
      ##########################################################################
      ## 2-2 리셋 코드
      #########################################################################
      #리셋 버튼을 누르면 기존 대화 내용을 모두 삭제하기 위해 st.session_state['chat']과
      #st.session_state['message']의 session_state를 초기화 한다.

      st.session_state['chat']=[]
      st.session_state['messages'] = [{'role': 'system', 'content':'You are a thoughtful assistant. Respond to all in put in 25 word and answer in Korean'}]
      st.session_state['check_reset'] = True


##################################################################
#기능 구현 공간
##################################################################
#기능 구현 영역을 두개의 영역으로 분할한다. 각 분할한 영역의 이름은 col1, col2로 지정한다.
  col1, col2 = st.columns(2)
  with col1:
    #왼쪽 영역 작성
    st.subheader('질문하기')
    ########################################################################
    ## 3. 스트림릿 오디오 레코더를 활용하여 음성 녹음하기
    ## 3-1 사용자의 음성 입력받기 및 재성 버튼 생성하기
    ########################################################################
    ## 음성 녹음 아이콘 추가
    # audiorecorder(start, stop, pause)
    audio = audiorecorder('클릭하여 녹음하기','녹음중...')

    if (audio.duration_seconds >0) and (st.session_state['check_reset']==False):
      #음성 재생
      st.audio(audio.export().read())

      #음원 파일에서 텍스트 추출
      question = STT(audio)

      #채팅을 시각화 하기 위해 질문 내용 저장
      now = datetime.now().strftime('%H:%M')
      st.session_state['chat'] = st.session_state['chat']+ [('user', now, question)]
      #GPT모델에 넣을 프롬프트를 위해 질문 내용 저장
      st.session_state['messages'] = st.session_state['messages']+ [{'role':'user', 'content':question}]
    ####################################################################

  with col2:
    #오른쪽 영역
    st.subheader('질문/답변')
    ########################################################
    ## 5. ChatGPT API로 질문하고 답변 구하기
    #######################################
    ## 5-1 ChatGPT API를 활용하여 답변 구하기
    ######################################
    if (audio.duration_seconds>0) and (st.session_state['check_reset']==False):
      #Chat GPT에게 답변 얻기
      response = ask_gpt(st.session_state['messages'],model)

      #GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
      st.session_state['messages'] = st.session_state['messages']+ [{'role':'system','content':response}] 

      #채팅 시각화를 위한 답변 내용 저장
      now = datetime.now().strftime('%H:%M')
      st.session_state['chat'] = st.session_state['chat']+ [('bot', now, response)]

      #########################################################
      ## 5-2 대화 내용을 채팅 형식으로 시각화 하기
      #########################################################
      # 채팅 형식으로 시각화 하기
      for sender, time, message in st.session_state["chat"]:
        if sender == "user":
          st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
          st.write("")
        else:
          st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
          st.write("")


      # gTTS를 활용하여 음성 파일 생성 및 재생
      TTS(response)

    else:
      st.session_state['check_reset'] = False


###################################################################

if __name__ == '__main__':
  main()

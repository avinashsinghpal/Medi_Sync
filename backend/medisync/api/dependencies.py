from fastapi import Request

# Stubs for dependency injection of services

async def get_patient_manager(request: Request):
    return request.app.state.patient_manager

async def get_appointment_system(request: Request):
    return request.app.state.appointment_system

async def get_doctor_dashboard(request: Request):
    return request.app.state.doctor_dashboard

async def get_nlp_engine(request: Request):
    return request.app.state.nlp_engine

async def get_priority_engine(request: Request):
    return request.app.state.priority_engine

async def get_speech_processor(request: Request):
    return request.app.state.speech_processor

# Auth dependency stubs

async def get_current_user(request: Request):
    # Stub for current user authentication
    pass

async def get_current_doctor(request: Request):
    # Stub for current doctor authentication
    pass

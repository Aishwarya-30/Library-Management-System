from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import motor.motor_asyncio as aiomotor
from urllib.parse import quote_plus

username = quote_plus("LibraryManagement")
password = quote_plus("Aishwarya19")

app = FastAPI()
client = aiomotor.AsyncIOMotorClient("mongodb://<username>:<password>@ac-hm49tta-shard-00-00.eher902.mongodb.net:27017,ac-hm49tta-shard-00-01.eher902.mongodb.net:27017,ac-hm49tta-shard-00-02.eher902.mongodb.net:27017/?ssl=true&replicaSet=atlas-w003l5-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0")
db = client.library
students_collection = db.students

class Address(BaseModel):
    city: str
    country: str


class Student(BaseModel):
    name: str
    age: int
    address: Address


@app.post("/students/", response_model=dict)
async def create_students(students: List[Student]):
    student_dicts = [student.dict() for student in students]
    result = await students_collection.insert_many(student_dicts)
    return {"ids": [str(id) for id in result.inserted_ids]}

@app.get("/")
async def root():
    return {"message": "Welcome to your FastAPI Student Library App!"}

@app.get("/students/", response_model=dict)
async def read_students(country: Optional[str] = None, age: Optional[int] = None):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    cursor = students_collection.find(query)
    students = []
    async for student in cursor:
        del student["_id"]
        students.append(student)
    return {"data": students}


@app.get("/students/{student_id}", response_model=dict)
async def read_student(student_id: str):
    student = await students_collection.find_one({"_id": student_id})
    if student:
        del student["_id"]
        return {"data": student}
    else:
        raise HTTPException(status_code=404, detail="Student not found")


@app.patch("/students/{student_id}", response_model=dict)
async def update_student(student_id: str, updated_student: Student):
    result = await students_collection.replace_one({"_id": student_id}, updated_student.dict())
    if result.matched_count == 1:
        return {"data": updated_student}
    else:
        raise HTTPException(status_code=404, detail="Student not found")


@app.delete("/students/{student_id}", response_model=dict)
async def delete_student(student_id: str):
    result = await students_collection.delete_one({"_id": student_id})
    if result.deleted_count == 1:
        return {"data": {"message": "Student deleted"}}
    else:
        raise HTTPException(status_code=404, detail="Student not found")
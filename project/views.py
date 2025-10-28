import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PaperSerializer
from .models import get_papers_collection, Login, AddUser, DoesUserExist, CreateJWTToken
import logging
import re
import os
from google import genai
from bson import ObjectId
from .middleware import jwt_required
import requests
import pdfplumber
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)
client = genai.Client(api_key="AIzaSyAaJcvE8zjU1tR_E-e5672Tx7A01cpX8BU")

def LLMRequest(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text
    except Exception as e:
        logger.error(f"LLM request failed: {str(e)}")
        return "Error generating AI response."

class LogInView(APIView):
    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']

        if not username or not password:
            return Response(
                {"error": "You are missing parameters!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

        if not DoesUserExist(username):
            return Response(
                {"error": "The username you entered does not exist!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        valid_password = Login(username, password)

        if not valid_password:
            return Response(
                {"error": "Incorrect password!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        token = CreateJWTToken(username)

        return Response({
            "access_token": token,
            "username": username,
        }, status=status.HTTP_200_OK)

class SignUpView(APIView):
    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        email = request.data['email']

        if not username or not password or not email:
            return Response(
                {"error": "You are missing parameters!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if len(password) < 8:
            return Response(
                {"error": "Your password is less than 8 characters!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if DoesUserExist(username):
            return Response(
                {"error": "The username you chose has already been taken!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if email.count('@') != 1: 
            return Response(
                {"error": "You chose an invalid email!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        AddUser(username, password, email)
        print(f"User '{username}' created successfully.")

        token = CreateJWTToken(username)

        return Response({
            "access_token": token,
            "username": username,
        }, status=status.HTTP_200_OK)

class PaperListView(APIView):
    def get(self, request):
        try:
            papers = get_papers_collection()

            if papers is None:
                return Response(
                    {"error": "Database connection failed. Please check MongoDB connection."}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            search_string = request.GET.get('search', '').strip()
            domain = request.GET.get('domain', '').strip().lower()
            subdomain = request.GET.get('subdomain', '').strip().lower()
            case_sensitive = request.GET.get('case_sensitive', 'false').lower() == 'true'
            
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:  
                page_size = 20
            
            query = self._build_search_query(search_string, domain, subdomain, case_sensitive)
            total_count = papers.count_documents(query)
            skip = (page - 1) * page_size
            cursor = papers.find(query).skip(skip).limit(page_size)
            data = list(cursor)
            
            if not data:
                return Response({
                    "results": [],
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total_count": total_count,
                        "total_pages": 0
                    },
                    "search_info": {
                        "search_string": search_string,
                        "domain": domain,
                        "subdomain": subdomain,
                        "case_sensitive": case_sensitive
                    }
                })
            
            for item in data:
                if '_id' in item:
                    item['id'] = str(item['_id'])

                    del item['_id']

            validated_data = []

            for item in data:
                validated_data.append(item)
            
            serializer = PaperSerializer(validated_data, many=True)
            total_pages = (total_count + page_size - 1) // page_size
            
            return Response({
                "results": serializer.data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                },
                "search_info": {
                    "search_string": search_string,
                    "domain": domain,
                    "subdomain": subdomain,
                    "case_sensitive": case_sensitive
                }
            })
            
        except ValueError as e:
            logger.error(f"Invalid pagination parameters: {str(e)}")

            return Response(
                {"error": "Invalid pagination parameters"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error fetching papers: {str(e)}")

            return Response(
                {"error": "An error occurred while fetching papers"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_search_query(self, search_string, domain, subdomain, case_sensitive):
        query = {}
        
        if domain:
            query["domain"] = {"$regex": domain, "$options": "i"}
        
        if subdomain:
            query["subdomain"] = {"$regex": subdomain, "$options": "i"}
        
        if search_string:
            try:
                re.compile(search_string)
                regex_options = "" if case_sensitive else "i"
                
                text_query = {
                    "$or": [
                        {"title": {"$regex": search_string, "$options": regex_options}},
                        {"summary": {"$regex": search_string, "$options": regex_options}},
                        {"author": {"$regex": search_string, "$options": regex_options}}
                    ]
                }
                
                if query:
                    query = {"$and": [query, text_query]}
                else:
                    query = text_query
                    
            except re.error:
                logger.warning(f"Invalid regex pattern: {search_string}, treating as plain text")
                regex_options = "" if case_sensitive else "i"
                
                escaped_search = re.escape(search_string)
                
                text_query = {
                    "$or": [
                        {"title": {"$regex": escaped_search, "$options": regex_options}},
                        {"summary": {"$regex": escaped_search, "$options": regex_options}},
                        {"author": {"$regex": escaped_search, "$options": regex_options}}
                    ]
                }
                
                if query:
                    query = {"$and": [query, text_query]}
                else:
                    query = text_query
        
        return query

class PaperDetailView(APIView):
    def get_object(self, id):
        try:
            papers = get_papers_collection()

            return papers.find_one({"_id": ObjectId(id)})
        except:
            return None

    #@jwt_required
    def get(self, request, id):
        try:
            paper = self.get_object(id)

            if not paper:
                return Response({"error": "Paper not found"}, status=status.HTTP_404_NOT_FOUND)
            
            paper['id'] = paper['_id']
            serializer = PaperSerializer(paper)

            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching paper {id}: {str(e)}")

            return Response(
                {"error": "An error occurred while fetching the paper"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, id):
        paper = self.get_object(id)

        if not paper:
            return Response({"error": "Paper not found"}, status=status.HTTP_404_NOT_FOUND)
        
        action = request.data.get("action")

        if action == "summarize":
            pdf_url = paper.get('pdf_link')
            if not pdf_url:
                return Response({"error": "No PDF link available"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Download the PDF
                response = requests.get(pdf_url)
                response.raise_for_status()

                # Open PDF from bytes
                with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                    full_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
                
                if not full_text.strip():
                    return Response({"error": "PDF is empty or could not extract text"}, status=status.HTTP_400_BAD_REQUEST)

                # Create prompt for LLM
                prompt = f"Summarize this academic paper for a student:\n{full_text}"
                summary = LLMRequest(prompt)

                return Response({"data": summary})
            except requests.RequestException as e:
                return Response({"error": f"Failed to fetch PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Error processing PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif action == "explain_term":
            term = request.data.get("term")

            if not term:
                return Response({"error": "Missing term parameter"}, status=status.HTTP_400_BAD_REQUEST)
            
            prompt = f"Explain the following academic term in simple terms: {term}"
            explanation = LLMRequest(prompt)

            return Response({"data": explanation})
        
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class PaperSearchView(APIView):    
    def get(self, request):
        try:
            papers = get_papers_collection()

            if papers is None:
                return Response(
                    {"error": "Database connection failed. Please check MongoDB connection."}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            search_string = request.GET.get('search', '').strip()
            title_search = request.GET.get('title', '').strip()
            summary_search = request.GET.get('summary', '').strip()
            author_search = request.GET.get('author', '').strip()
            domain = request.GET.get('domain', '').strip().lower()
            subdomain = request.GET.get('subdomain', '').strip().lower()
            case_sensitive = request.GET.get('case_sensitive', 'false').lower() == 'true'
            exact_match = request.GET.get('exact_match', 'false').lower() == 'true'
            
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 20
            
            query = self._build_advanced_search_query(
                search_string, title_search, summary_search, author_search,
                domain, subdomain, case_sensitive, exact_match
            )
            
            total_count = papers.count_documents(query)
            skip = (page - 1) * page_size
            cursor = papers.find(query).skip(skip).limit(page_size)
            data = list(cursor)
            
            if not data:
                return Response({
                    "results": [],
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total_count": total_count,
                        "total_pages": 0
                    },
                    "search_info": {
                        "search_string": search_string,
                        "title_search": title_search,
                        "summary_search": summary_search,
                        "author_search": author_search,
                        "domain": domain,
                        "subdomain": subdomain,
                        "case_sensitive": case_sensitive,
                        "exact_match": exact_match
                    }
                })

            for item in data:
                if '_id' in item:
                    item['id'] = str(item['_id'])

                    del item['_id']
            
            validated_data = []

            for item in data:
                validated_data.append(item)
            
            serializer = PaperSerializer(validated_data, many=True)
            total_pages = (total_count + page_size - 1) // page_size
            
            return Response({
                "results": serializer.data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                },
                "search_info": {
                    "search_string": search_string,
                    "title_search": title_search,
                    "summary_search": summary_search,
                    "author_search": author_search,
                    "domain": domain,
                    "subdomain": subdomain,
                    "case_sensitive": case_sensitive,
                    "exact_match": exact_match
                }
            })
            
        except ValueError as e:
            logger.error(f"Invalid search parameters: {str(e)}")

            return Response(
                {"error": "Invalid search parameters"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error searching papers: {str(e)}")

            return Response(
                {"error": "An error occurred while searching papers"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_advanced_search_query(self, search_string, title_search, summary_search, 
                                   author_search, domain, subdomain, case_sensitive, exact_match):
        query = {}
        conditions = []
        
        if domain:
            if exact_match:
                query["domain"] = domain
            else:
                query["domain"] = {"$regex": domain, "$options": "i"}
        
        if subdomain:
            if exact_match:
                query["subdomain"] = subdomain
            else:
                query["subdomain"] = {"$regex": subdomain, "$options": "i"}
        
        if title_search:
            conditions.append(self._build_field_query("title", title_search, case_sensitive, exact_match))
        
        if summary_search:
            conditions.append(self._build_field_query("summary", summary_search, case_sensitive, exact_match))
        
        if author_search:
            conditions.append(self._build_field_query("author", author_search, case_sensitive, exact_match))
        
        if search_string:
            search_conditions = []

            for field in ["title", "summary", "author"]:
                search_conditions.append(self._build_field_query(field, search_string, case_sensitive, exact_match))
            
            if search_conditions:
                conditions.append({"$or": search_conditions})
        
        if conditions:
            if len(conditions) == 1:
                query.update(conditions[0])
            else:
                query["$and"] = conditions
        
        return query
    
    def _build_field_query(self, field, search_term, case_sensitive, exact_match):
        if exact_match:
            return {field: search_term}
        else:
            regex_options = "" if case_sensitive else "i"

            try:
                re.compile(search_term)

                return {field: {"$regex": search_term, "$options": regex_options}}
            except re.error:
                escaped_search = re.escape(search_term)

                return {field: {"$regex": escaped_search, "$options": regex_options}}
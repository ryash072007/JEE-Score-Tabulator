from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import os
import tempfile
import traceback
import time

from .forms import JEEPdfUploadForm
from .jee_utils import JEECalculator
from .models import JEEPdfUpload, JEEScores

def home(request):
    """Home page with upload form"""
    form = JEEPdfUploadForm()
    return render(request, 'jeecalculator/home.html', {'form': form})

def upload_and_process(request):
    """Handle file uploads and process them"""
    start_time = time.time()
    print(f"\n\nDEBUG: Starting upload_and_process at {time.strftime('%H:%M:%S')}")
    
    if request.method == 'POST':
        print(f"DEBUG: Received POST request with files: {request.FILES.keys()}")
        form = JEEPdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print("DEBUG: Form is valid, processing files...")
            try:
                # Save the uploaded files
                upload_instance = form.save()
                print(f"DEBUG: Files saved, instance ID: {upload_instance.id}")
                
                # Get file paths
                answer_key_path = upload_instance.answer_key.path
                student_response_path = upload_instance.student_response.path
                
                print(f"DEBUG: Answer key path: {answer_key_path}")
                print(f"DEBUG: Answer key file exists: {os.path.exists(answer_key_path)}")
                print(f"DEBUG: Answer key file size: {os.path.getsize(answer_key_path)} bytes")
                print(f"DEBUG: Answer key file type: {os.path.splitext(answer_key_path)[1]}")
                
                print(f"DEBUG: Student response path: {student_response_path}")
                print(f"DEBUG: Student response file exists: {os.path.exists(student_response_path)}")
                print(f"DEBUG: Student response file size: {os.path.getsize(student_response_path)} bytes")
                print(f"DEBUG: Student response file type: {os.path.splitext(student_response_path)[1]}")
                
                # Inspect content of the files (first few bytes)
                try:
                    with open(answer_key_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(200)
                        print(f"DEBUG: Answer key file content (first 200 chars): {content}")
                except Exception as e:
                    print(f"DEBUG: Error reading answer key file text: {str(e)}")
                    # Try binary mode
                    with open(answer_key_path, 'rb') as f:
                        content = f.read(50)
                        print(f"DEBUG: Answer key binary content (first 50 bytes): {content}")
                
                try:
                    with open(student_response_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(200)
                        print(f"DEBUG: Student response file content (first 200 chars): {content}")
                except Exception as e:
                    print(f"DEBUG: Error reading student response file text: {str(e)}")
                    # Try binary mode
                    with open(student_response_path, 'rb') as f:
                        content = f.read(50)
                        print(f"DEBUG: Student response binary content (first 50 bytes): {content}")
                
                # Create JEE calculator instance with pattern adjustments
                print(f"DEBUG: Creating JEECalculator with pattern_q={upload_instance.pattern_q}, pattern_a={upload_instance.pattern_a}")
                calculator = JEECalculator(
                    upload_instance.pattern_q,
                    upload_instance.pattern_a
                )
                
                # Process files
                print("DEBUG: Processing answer key file...")
                answer_key_data = calculator.get_answer_key(answer_key_path)
                print(f"DEBUG: Answer key processing complete, data type: {type(answer_key_data)}, length: {len(answer_key_data) if isinstance(answer_key_data, list) else 'N/A'}")
                
                print("DEBUG: Processing student response file...")
                student_responses = calculator.get_student_responses(student_response_path)
                print(f"DEBUG: Student response processing complete, data type: {type(student_responses)}, length: {len(student_responses) if isinstance(student_responses, list) else 'N/A'}")
                
                # Check if there was an error in processing
                if isinstance(answer_key_data, str):
                    error_message = f"Error processing answer key: {answer_key_data}"
                    print(f"DEBUG: ERROR: {error_message}")
                    raise ValueError(error_message)
                    
                if isinstance(student_responses, str):
                    error_message = f"Error processing student responses: {student_responses}"
                    print(f"DEBUG: ERROR: {error_message}")
                    raise ValueError(error_message)
                
                if not answer_key_data:
                    error_message = "No data found in answer key file. Please check file format."
                    print(f"DEBUG: ERROR: {error_message}")
                    raise ValueError(error_message)
                    
                if not student_responses:
                    error_message = "No data found in student response file. Please check file format."
                    print(f"DEBUG: ERROR: {error_message}")
                    raise ValueError(error_message)
                
                # Compare answers
                print(f"DEBUG: Comparing answers: {len(answer_key_data)} answer key items vs {len(student_responses)} student responses")
                results, summary = calculator.check_answers(answer_key_data, student_responses)
                print(f"DEBUG: Results generated: {len(results)} results, summary: {summary}")
                
                # Get subject-wise analysis
                print("DEBUG: Generating subject-wise analysis...")
                subjects = calculator.subject_wise_analysis(results)
                print(f"DEBUG: Subject analysis complete: {subjects}")
                
                # Store the results in session for displaying
                print("DEBUG: Storing results in session...")
                request.session['results'] = results
                request.session['summary'] = summary
                request.session['subjects'] = subjects
                
                # Print results to console (as requested)
                print("--- JEE Score Analysis ---")
                print(f"Total Questions: {summary['total_questions']}")
                print(f"Correct: {summary['correct']}, Incorrect: {summary['incorrect']}, Skipped: {summary['skipped']}")
                print(f"Total Score: {summary['score']}")
                print("\n--- Subject-wise Analysis ---")
                print(f"Mathematics: Correct: {subjects['math']['correct']}, Incorrect: {subjects['math']['incorrect']}, Score: {subjects['math']['score']}")
                print(f"Physics: Correct: {subjects['physics']['correct']}, Incorrect: {subjects['physics']['incorrect']}, Score: {subjects['physics']['score']}")
                print(f"Chemistry: Correct: {subjects['chemistry']['correct']}, Incorrect: {subjects['chemistry']['incorrect']}, Score: {subjects['chemistry']['score']}")
                
                JEEScores.objects.create(
                    name=calculator.name,
                    total_score=summary['score'],
                    correct_answers=summary['correct'],
                    incorrect_answers=summary['incorrect'],
                    unattempted_questions=summary['skipped'],
                    math_score=subjects['math']['score'],
                    physics_score=subjects['physics']['score'],
                    chemistry_score=subjects['chemistry']['score']
                )

                print("\n--- Detailed Results ---")
                for result in results[:10]:  # Print only first 10 for brevity
                    print(result)
                print(f"(... {len(results) - 10} more results ...)" if len(results) > 10 else "")
                
                elapsed_time = time.time() - start_time
                print(f"DEBUG: Processing completed in {elapsed_time:.2f} seconds")
                
                # Redirect to results page
                print("DEBUG: Redirecting to results page")
                return redirect('results')
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                print(f"DEBUG: Exception occurred: {str(e)}")
                traceback.print_exc()  # Print the full traceback for debugging
                messages.error(request, error_message)
                return render(request, 'jeecalculator/home.html', {'form': form, 'error': error_message})
        else:
            print(f"DEBUG: Form is invalid: {form.errors}")
            messages.error(request, "Form submission error. Please check your inputs.")
    else:
        print("DEBUG: GET request, displaying empty form")
        form = JEEPdfUploadForm()
    
    return render(request, 'jeecalculator/home.html', {'form': form})

def results(request):
    """Display analysis results"""
    print("\nDEBUG: Results view called")
    results = request.session.get('results', [])
    summary = request.session.get('summary', {})
    subjects = request.session.get('subjects', {})
    
    print(f"DEBUG: Retrieved from session - results: {len(results)} items, summary: {summary}")
    
    context = {
        'results': results,
        'summary': summary,
        'subjects': subjects
    }
    
    return render(request, 'jeecalculator/results.html', context)

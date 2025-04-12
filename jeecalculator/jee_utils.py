import os
import PyPDF2
from io import BytesIO
import re
import traceback
from jeecalculator.formatter import format_html

class JEECalculator:
    def __init__(self, q_pat, a_pat):
        self.q_pat = q_pat  # Question pattern adjustment
        self.a_pat = a_pat  # Answer pattern adjustment
        self.name = ""
        self.test_date = ""
        self.test_time = ""
        print(f"DEBUG: JEECalculator initialized with q_pat={q_pat}, a_pat={a_pat}")

    def get_answer_key(self, file_path):
        """Parse the answer key from PDF or HTML file"""
        print(f"\nDEBUG: get_answer_key called with file_path: {file_path}")
        print(f"DEBUG: File exists: {os.path.exists(file_path)}")
        print(f"DEBUG: File size: {os.path.getsize(file_path)} bytes")
        print(f"DEBUG: File extension: {os.path.splitext(file_path)[1]}")
        
        data = []
        try:
            # Check if file is PDF or HTML based on extension
            if file_path.lower().endswith('.pdf'):
                print(f"DEBUG: Processing PDF answer key: {file_path}")
                # Process PDF answer key
                with open(file_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    print(f"DEBUG: PDF has {len(reader.pages)} pages")
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    
                    print(f"DEBUG: Extracted text length: {len(text)} characters")
                    print(f"DEBUG: First 200 chars of text: {text[:200]}")
                    
                    # Parse the PDF text to extract question-answer pairs
                    lines = text.split('\n')
                    print(f"DEBUG: Split text into {len(lines)} lines")
                    current_question = None
                    
                    for line in lines:
                        # Look for question numbers and answers
                        q_match = re.search(r'Question ID\s*:\s*(\d+)', line)
                        a_match = re.search(r'Correct Option\s*:\s*(\d+)', line)
                        
                        if q_match:
                            current_question = q_match.group(1)
                            data.append([current_question])
                            print(f"DEBUG: Found question ID: {current_question}")
                        elif a_match and current_question and len(data) > 0 and len(data[-1]) == 1:
                            answer = a_match.group(1)
                            data[-1].append(answer)
                            print(f"DEBUG: Found answer for question {current_question}: {answer}")
                            current_question = None
            else:
                # Improved HTML processing using direct approach from jeeCalc.py
                print(f"DEBUG: Processing HTML answer key: {file_path}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as ans_key:
                    content = ans_key.read()
                    content = format_html(content)  # Format HTML for better parsing
                    lines = content.split('\n')
                    print(f"DEBUG: HTML content has {len(lines)} lines")
                    
                    for line in lines:
                        if "QuestionNo" in line:
                            greater_than_pos = line.find('>')
                            less_than_pos = line.find('</')
                            if greater_than_pos != -1 and less_than_pos != -1:
                                q = line[greater_than_pos+1:less_than_pos]
                                # Extract the last 3 digits, but ensure we get the full number if needed
                                q_num = q.strip()
                                data.append([q_num])
                                print(f"DEBUG: Found question number: {q_num}")
                        
                        if "lbl_RAnswer" in line:
                            greater_than_pos = line.find('>')
                            less_than_pos = line.find('</')
                            if greater_than_pos != -1 and less_than_pos != -1 and len(data) > 0:
                                a = line[greater_than_pos+1:less_than_pos]
                                # Extract the last 3 digits, but ensure we get the full number if needed
                                ans = a.strip()
                                if len(data[-1]) == 1:  # Make sure we have a question to attach to
                                    data[-1].append(ans)
                                    print(f"DEBUG: Found answer: {ans} for question {data[-1][0]}")
                    
                    # If the standard parsing didn't work, try alternative patterns
                    if not data:
                        print("DEBUG: Standard parsing didn't find data, trying alternative methods")
                        # Use the patterns from your existing code as fallback
                        # Pattern 1: Table format, Pattern 2: Direct regex search, etc.
                        table_pattern = r'<table[^>]*>(.*?)</table>'
                        tables = re.findall(table_pattern, content, re.DOTALL)
                        
                        for table in tables:
                            # Look for rows with question numbers and answers
                            row_pattern = r'<tr[^>]*>(.*?)</tr>'
                            rows = re.findall(row_pattern, table, re.DOTALL)
                            
                            for row in rows:
                                # Extract cells
                                cell_pattern = r'<td[^>]*>(.*?)</td>'
                                cells = re.findall(cell_pattern, row, re.DOTALL)
                                
                                if len(cells) >= 2:
                                    # First cell might be question number, second might be answer
                                    q_num = re.sub(r'<[^>]*>', '', cells[0]).strip()
                                    ans = re.sub(r'<[^>]*>', '', cells[1]).strip()
                                    
                                    if q_num.isdigit():
                                        data.append([q_num, ans])
                                        print(f"DEBUG: From table - Question: {q_num}, Answer: {ans}")
                        
                        # Pattern 3: Direct search for specific patterns in text
                        if not data:
                            print("DEBUG: Trying direct text pattern search")
                            # Look for patterns like "Question(Number): Answer"
                            q_a_pattern = r'(\d+)\s*[.:]\s*([A-D0-9]+)'
                            matches = re.findall(q_a_pattern, content)
                            
                            if matches:
                                for q_num, ans in matches:
                                    data.append([q_num.strip(), ans.strip()])
                                    print(f"DEBUG: Direct pattern - Question: {q_num}, Answer: {ans}")
            
            # Print the data being processed to console for debugging
            print(f"\nDEBUG: Final answer key data has {len(data)} questions")
            for i, qa in enumerate(data[:10]):  # Print first 10 for debugging
                print(f"DEBUG: Q{i+1}: {qa}")
            
            if len(data) > 0:
                print(f"DEBUG: Applying pattern adjustments with q_pat={self.q_pat}, a_pat={self.a_pat}")
                self.apply_pattern(data)
                
                # New code: Print all question IDs after pattern adjustment
                print("\n--- ANSWER KEY QUESTION IDs (AFTER PATTERN ADJUSTMENT) ---")
                all_question_ids = [item[0] for item in data]
                
                # Print in groups of 10 for readability
                for i in range(0, len(all_question_ids), 10):
                    group = all_question_ids[i:i+10]
                    print(f"IDs {i+1}-{i+len(group)}: {', '.join(group)}")
                    
                # For easy copy-paste debugging
                print("\nALL IDs (comma-separated):")
                print(','.join(all_question_ids))
            else:
                print("DEBUG: No data to apply pattern to!")
                
            return data
        except Exception as e:
            print(f"ERROR in get_answer_key: {str(e)}")
            traceback.print_exc()
            return f"Error processing answer key: {str(e)}"

    def apply_pattern(self, datas):
        """Apply pattern adjustments to question and answer IDs"""
        print(f"DEBUG: apply_pattern called with {len(datas)} items")
        try:
            for i, item in enumerate(datas):
                if len(item) < 2:
                    print(f"DEBUG: Skipping pattern adjustment for incomplete item {i}: {item}")
                    continue
                
                print(f"DEBUG: Original data item {i}: {item}")
                
                # Get the question number
                q_num = int(item[0])
                
                # Always apply question pattern adjustment
                item[0] = str(abs(self.q_pat + q_num))
                
                # Check if question is in a special range based on INDEX, not question number
                # This matches the original jeeCalc.py logic
                special_range = (i in range(20, 25) or 
                              i in range(45, 50) or 
                              i in range(70, 75))
                
                if special_range:
                    # For special range questions, don't modify the answer
                    print(f"DEBUG: Item {i} (Q{q_num}) is in special range - answer pattern NOT applied")
                else:
                    # For normal questions, apply answer pattern adjustment
                    if isinstance(item[1], str) and "," in item[1]:
                        # Handle comma-separated answers
                        ans_parts = item[1].split(",")
                        for j in range(len(ans_parts)):
                            try:
                                ans_parts[j] = str(abs(self.a_pat + int(ans_parts[j].strip())))
                            except ValueError:
                                print(f"DEBUG: Could not convert '{ans_parts[j]}' to int in item {i}")
                        item[1] = ",".join(ans_parts)
                    else:
                        # Handle single answers
                        if isinstance(item[1], str):
                            try:
                                original_ans = item[1]
                                item[1] = str(abs(self.a_pat + int(item[1])))
                                print(f"DEBUG: Adjusted answer for Q{q_num}: {original_ans} → {item[1]}")
                            except ValueError:
                                print(f"DEBUG: Could not convert '{item[1]}' to int in item {i}")
                
                print(f"DEBUG: Adjusted item {i}: {item}")
        except Exception as e:
            print(f"ERROR in apply_pattern: {str(e)}")
            traceback.print_exc()

    def get_student_responses(self, file_path):
        """Parse student responses from PDF or HTML file"""
        print(f"\nDEBUG: get_student_responses called with file_path: {file_path}")
        print(f"DEBUG: File exists: {os.path.exists(file_path)}")
        print(f"DEBUG: File size: {os.path.getsize(file_path)} bytes")
        print(f"DEBUG: File extension: {os.path.splitext(file_path)[1]}")
        
        data = []
        try:
            # Check file type based on extension
            if file_path.lower().endswith('.pdf'):
                print(f"DEBUG: Processing PDF student responses: {file_path}")
                # Process PDF student responses
                if isinstance(file_path, BytesIO):
                    pdf_file = file_path
                else:
                    pdf_file = open(file_path, 'rb')
                    
                reader = PyPDF2.PdfReader(pdf_file)
                print(f"DEBUG: PDF has {len(reader.pages)} pages")
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

                print(f"DEBUG: Extracted text length: {len(text)} characters")
                print(f"DEBUG: First 200 chars of text: {text[:200]}")
                
                lines = text.split('\n')
                print(f"DEBUG: Split text into {len(lines)} lines")
                type_q = None
                for line in lines:
                    if "Question Type :MCQ" in line:
                        type_q = "MCQ"
                        print(f"DEBUG: Found MCQ question type marker")
                        continue
                    if "Question Type :SA" in line:
                        type_q = "SA"
                        print(f"DEBUG: Found SA question type marker")
                        continue
                    if "Question ID :" in line:
                        qid = line[line.find(":") + 1:].strip()
                        data.append([qid])
                        print(f"DEBUG: Found question ID: {qid}")
                        continue
                    if type_q == "MCQ":
                        if "Chosen Option :" in line:
                            ans = line[line.find(":") + 1:].strip()
                            if ans[:2] == "--":
                                ans = "--"
                            if "Q" in ans:
                                ans = ans[:ans.find("Q")]
                            if "S" in ans:
                                ans = ans[:ans.find("S")]
                            if len(data) > 0:
                                data[-1].append(ans)
                                print(f"DEBUG: Found chosen option for question {data[-1][0]}: {ans}")
                            continue
                        
                        if "Option 1 ID :" in line and len(data) > 0:
                            data[-1].append([line[line.find(":") + 1:].strip()])
                            print(f"DEBUG: Found option 1 ID for question {data[-1][0]}: {data[-1][-1][0]}")
                            continue
                        if ("Option 2 ID :" in line or "Option 3 ID :" in line or "Option 4 ID :" in line) and len(data) > 0 and len(data[-1]) >= 3:
                            data[-1][-1].append(line[line.find(":") + 1:].strip())
                            print(f"DEBUG: Found additional option ID for question {data[-1][0]}: {data[-1][-1][-1]}")
                            continue
                    if type_q == "SA":
                        if "Answer :" in line and len(data) > 0:
                            ans = line[line.find(":") + 1:].strip()
                            data[-1].append(ans)
                            print(f"DEBUG: Found SA answer for question {data[-1][0]}: {ans}")
                            continue
                
                if not isinstance(file_path, BytesIO):
                    pdf_file.close()
            else:
                # Improved HTML processing based on jeeCalc.py
                print(f"DEBUG: Processing HTML student responses: {file_path}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as html_file:
                    content = html_file.read()
                    content = format_html(content)  # Format HTML for better parsing
                    lines = content.split('\n')
                    print(f"DEBUG: HTML content has {len(lines)} lines")
                    
                    q_next = False
                    a_next = False
                    id_next = False
                    non_mcq = False
                    non_mcq_q_next = False
                    
                    # Using direct parsing approach from jeeCalc.py
                    for i, line in enumerate(lines):
                        if "Candidate Name" in line:
                            self.name = lines[i+1].strip().replace("<td>", "").replace("</td>", "")
                        if "Test Date" in line:
                            self.test_date = lines[i+1].strip().replace("<td>", "").replace("</td>", "")
                        if "Test Time" in line:
                            self.test_time = lines[i+1].strip().replace("<td>", "").replace("</td>", "")
                        if "Question ID :" in line:
                            q_next = True
                            continue
                            
                        if q_next:
                            q_next = False
                            greater_than_pos = line.find('>')
                            less_than_pos = line.find('</')
                            
                            if greater_than_pos != -1 and less_than_pos != -1:
                                if non_mcq_q_next:
                                    non_mcq_q_next = False
                                    q_id = line[greater_than_pos+1:less_than_pos].strip()
                                    data[-1].insert(0, q_id)
                                    print(f"DEBUG: Found non-MCQ question ID: {q_id}")
                                    continue
                                else:
                                    q_id = line[greater_than_pos+1:less_than_pos].strip()
                                    data.append([q_id])
                                    print(f"DEBUG: Found question ID: {q_id}")
                            
                        if "Chosen Option :" in line:
                            a_next = True
                            continue
                            
                        if "Given Answer :" in line:
                            non_mcq = True
                            continue
                            
                        if non_mcq:
                            non_mcq = False
                            greater_than_pos = line.find('>')
                            less_than_pos = line.find('</')
                            
                            if greater_than_pos != -1 and less_than_pos != -1:
                                ans = line[greater_than_pos+1:less_than_pos].strip()
                                data.append([ans])
                                print(f"DEBUG: Found non-MCQ answer: {ans}")
                            continue
                            
                        if '<td class="bold">SA</td>' in line:
                            non_mcq_q_next = True
                            continue
                            
                        if a_next:
                            a_next = False
                            greater_than_pos = line.find('>')
                            less_than_pos = line.find('</')
                            
                            if greater_than_pos != -1 and less_than_pos != -1:
                                ans = line[greater_than_pos+1:less_than_pos].strip()
                                if len(data) > 0:
                                    data[-1].append(ans if ans != "--" else "--")
                                    print(f"DEBUG: Found chosen option: {ans} for question {data[-1][0]}")
                            
                        if "Option 1 ID :" in line and len(data) > 0:
                            id_next = True
                            data[-1].append([])
                            continue
                            
                        if "Option 2 ID :" in line or "Option 3 ID :" in line or "Option 4 ID :" in line:
                            id_next = True
                            continue
                            
                        if id_next:
                            id_next = False
                            greater_than_pos = line.find('>')
                            less_than_pos = line.find('</')
                            
                            if greater_than_pos != -1 and less_than_pos != -1:
                                option_id = line[greater_than_pos+1:less_than_pos].strip()
                                if len(data) > 0 and len(data[-1]) >= 2:
                                    data[-1][-1].append(option_id)
                                    print(f"DEBUG: Found option ID: {option_id} for question {data[-1][0]}")
                    
                    # If direct parsing didn't work, fall back to regex-based patterns
                    if not data:
                        print("DEBUG: Direct parsing didn't find data, trying regex patterns")
                        # Pattern 1: Question ID and Chosen Option
                        question_pattern = r'Question ID\s*:\s*(\d+)'
                        chosen_pattern = r'Chosen Option\s*:\s*([^<\n]+)'
                        
                        question_matches = re.findall(question_pattern, content)
                        chosen_matches = re.findall(chosen_pattern, content)
                        
                        print(f"DEBUG: Found {len(question_matches)} question IDs with pattern '{question_pattern}'")
                        print(f"DEBUG: Found {len(chosen_matches)} chosen options with pattern '{chosen_pattern}'")
                        
                        # If we have both question IDs and chosen options, pair them
                        if question_matches and chosen_matches and len(question_matches) == len(chosen_matches):
                            for i in range(len(question_matches)):
                                qid = question_matches[i].strip()
                                chosen = chosen_matches[i].strip()
                                
                                # Format similar to the PDF processing
                                if chosen.startswith("--"):
                                    chosen = "--"
                                
                                data.append([qid, chosen])
                                print(f"DEBUG: Created data entry: [{qid}, {chosen}]")
            
            # Print a few sample responses for debugging
            print(f"\nDEBUG: Final student response data has {len(data)} entries")
            for i, resp in enumerate(data[:10]):  # Print first 10 for debugging
                print(f"DEBUG: Response {i+1}: {resp}")
                
            return data
        except Exception as e:
            print(f"ERROR in get_student_responses: {str(e)}")
            traceback.print_exc()
            return f"Error processing student responses: {str(e)}"

    def check_answers(self, answer_key, student_responses):
        """Compare student responses with answer key"""
        print(f"\nDEBUG: check_answers called with answer_key({len(answer_key)}) and student_responses({len(student_responses)})")
        
        skipped = 0
        correct = 0
        incorrect = 0
        outputs = []
        
        # Create a dictionary for quick lookup using last 3 digits
        answer_key_dict = {}
        for item in answer_key:
            q_id = item[0]
            # Extract last 3 digits or use full ID if shorter
            last_3_digits = q_id[-3:] if len(q_id) >= 3 else q_id
            answer_key_dict[last_3_digits] = item
        
        # Print all answer key IDs with their last 3 digits
        print("\nDEBUG: Answer key question IDs (showing last 3 digits):")
        for item in answer_key[:10]:  # Print first 10 for debugging
            last_3 = item[0][-3:] if len(item[0]) >= 3 else item[0]
            print(f"DEBUG: Full ID: {item[0]}, Last 3 digits: {last_3}")
            
        try:
            for i, student_ans in enumerate(student_responses):
                if not isinstance(student_ans, list) or len(student_ans) < 2:
                    outputs.append(f"Error with response {i+1}: Invalid format")
                    print(f"DEBUG: Invalid format for response {i+1}")
                    continue
                    
                # Get only the last 3 digits of student question ID
                student_q_id = student_ans[0]
                student_q_id_last3 = student_q_id[-3:] if len(student_q_id) >= 3 else student_q_id
                print(f"DEBUG: Student ID '{student_q_id}', last 3 digits: '{student_q_id_last3}'")
                
                # Lookup using the last 3 digits
                ans = answer_key_dict.get(student_q_id_last3)
                
                if ans:
                    print(f"DEBUG: ✓ Found match using last 3 digits - Student ID: {student_q_id} → Answer key ID: {ans[0]}")
                else:
                    print(f"DEBUG: ✗ NO MATCH for ID '{student_q_id}' (last 3: '{student_q_id_last3}')")
                    outputs.append(f"Q{i+1} (ID: {student_q_id}): No matching question found in answer key")
                    continue

                # Handle standard format [question_id, answer]
                if len(student_ans) == 2:
                    if student_ans[1] == "--":
                        skipped += 1
                        outputs.append(f"Q{i+1} (ID: {student_q_id}): Skipped")
                        continue
                    
                    # Check if answer is correct - FIXED LOGIC FOR COMMA-SEPARATED ANSWERS
                    correct_answer = ans[1]
                    if isinstance(correct_answer, list):
                        correct_answer_str = ", ".join(correct_answer)
                        is_correct = student_ans[1] in correct_answer
                    else:
                        correct_answer_str = correct_answer
                        # Handle comma-separated answers in the answer key
                        if "," in correct_answer:
                            correct_options = [opt.strip() for opt in correct_answer.split(",")]
                            is_correct = student_ans[1] in correct_options
                            print(f"DEBUG: Comma-separated answers found: {correct_options}")
                        else:
                            is_correct = student_ans[1] == correct_answer
                    
                    print(f"DEBUG: Student answer '{student_ans[1]}' vs correct '{correct_answer_str}': {'✓' if is_correct else '✗'}")
                    
                    if is_correct:
                        outputs.append(f"Q{i+1} (ID: {student_q_id}): Correct (Answer ID: {ans[1]}, Chosen: {student_ans[1]})")
                        correct += 1
                    else:
                        outputs.append(f"Q{i+1} (ID: {student_q_id}): Incorrect (Answer ID: {ans[1]}, Chosen: {student_ans[1]})")
                        incorrect += 1
                
                # Handle format [question_id, options_array, chosen_option] - ADD SIMILAR FIX HERE
                elif len(student_ans) == 3:
                    if student_ans[1] == "--" or student_ans[2] == "--":
                        skipped += 1
                        outputs.append(f"Q{i+1} (ID: {student_q_id}): Skipped")
                        continue
                    
                    try:
                        # Check if student_ans[1] is a list (options array)
                        if isinstance(student_ans[1], list):
                            option_index = int(student_ans[2]) - 1
                            if 0 <= option_index < len(student_ans[1]):
                                chosen_ans = student_ans[1][option_index]
                                print(f"DEBUG: Chosen option {student_ans[2]} maps to answer ID '{chosen_ans}'")
                            else:
                                print(f"DEBUG: Option index {option_index} out of range for options list: {student_ans[1]}")
                                outputs.append(f"Q{i+1} (ID: {student_q_id}): Invalid option index")
                                continue
                        else:
                            # If it's a string, try to use it directly
                            chosen_ans = str(student_ans[2])
                            print(f"DEBUG: Using direct chosen option: '{chosen_ans}'")
                        
                        # Now compare the chosen answer with the correct answer - FIXED LOGIC
                        if isinstance(ans[1], list):
                            is_correct = chosen_ans in ans[1]
                            correct_answer_str = ", ".join(ans[1])
                        else:
                            correct_answer_str = ans[1]
                            # Handle comma-separated answers
                            if "," in ans[1]:
                                correct_options = [opt.strip() for opt in ans[1].split(",")]
                                is_correct = chosen_ans in correct_options
                                print(f"DEBUG: Comma-separated answers found: {correct_options}")
                            else:
                                is_correct = chosen_ans == ans[1]
                        
                        print(f"DEBUG: Student answer '{chosen_ans}' vs correct '{correct_answer_str}': {'✓' if is_correct else '✗'}")
                        
                        if is_correct:
                            outputs.append(f"Q{i+1} (ID: {student_q_id}): Correct (Answer ID: {ans[1]}, Chosen: {chosen_ans})")
                            correct += 1
                        else:
                            outputs.append(f"Q{i+1} (ID: {student_q_id}): Incorrect (Answer ID: {ans[1]}, Chosen: {chosen_ans})")
                            incorrect += 1
                    except (IndexError, ValueError) as e:
                        outputs.append(f"Q{i+1} (ID: {student_q_id}): Error processing answer - {str(e)}")
                        print(f"DEBUG: Error processing answer: {str(e)}")
                else:
                    outputs.append(f"Q{i+1} (ID: {student_q_id}): Format error - unexpected number of elements ({len(student_ans)})")
                    print(f"DEBUG: Format error for question {i+1} - has {len(student_ans)} elements: {student_ans}")
            
            summary = {
                "correct": correct,
                "incorrect": incorrect,
                "skipped": 0,
                "score": correct * 4 - incorrect,
                "total_questions": len(student_responses)
            }
            
            print(f"\nDEBUG: Score analysis complete - Correct: {correct}, Incorrect: {incorrect}, Skipped: {skipped}")
            print(f"DEBUG: Total score: {correct * 4 - incorrect}")
            
            # Missing return statement was here!
            return outputs, summary
            
        except Exception as e:
            print(f"ERROR in check_answers: {str(e)}")
            traceback.print_exc()
            empty_summary = {"correct": 0, "incorrect": 0, "skipped": 0, "score": 0, "total_questions": 0}
            return [f"Error in check_answers: {str(e)}"], empty_summary

    def subject_wise_analysis(self, results):
        """Calculate subject-wise performance"""
        print(f"\nDEBUG: subject_wise_analysis called with {len(results)} results")
        
        math_c = math_i = phy_c = phy_i = chem_c = chem_i = 0
        math_s = phy_s = chem_s = 0
        
        try:
            # Assuming first 25 questions are math, next 25 are physics, last 25 are chemistry
            for i in range(min(25, len(results))):
                result = results[i]
                print(f"DEBUG: Math question {i+1} result: {result}")
                if "Correct" in result:
                    math_c += 1
                elif "Incorrect" in result:
                    math_i += 1
                elif "Skipped" in result:
                    math_s += 1
            
            for i in range(25, min(50, len(results))):
                result = results[i]
                print(f"DEBUG: Physics question {i+1} result: {result}")
                if "Correct" in result:
                    phy_c += 1
                elif "Incorrect" in result:
                    phy_i += 1
                elif "Skipped" in result:
                    phy_s += 1
            
            for i in range(50, min(75, len(results))):
                result = results[i]
                print(f"DEBUG: Chemistry question {i+1} result: {result}")
                if "Correct" in result:
                    chem_c += 1
                elif "Incorrect" in result:
                    chem_i += 1
                elif "Skipped" in result:
                    chem_s += 1
                    
            subjects = {
                "math": {"correct": math_c, "incorrect": math_i, "skipped": math_s, "score": math_c * 4 - math_i},
                "physics": {"correct": phy_c, "incorrect": phy_i, "skipped": phy_s, "score": phy_c * 4 - phy_i},
                "chemistry": {"correct": chem_c, "incorrect": chem_i, "skipped": chem_s, "score": chem_c * 4 - chem_i}
            }
            
            print(f"DEBUG: Subject-wise analysis:")
            print(f"DEBUG: Math: C={math_c}, I={math_i}, S={math_s}, Score={math_c * 4 - math_i}")
            print(f"DEBUG: Physics: C={phy_c}, I={phy_i}, S={phy_s}, Score={phy_c * 4 - phy_i}")
            print(f"DEBUG: Chemistry: C={chem_c}, I={chem_i}, S={chem_s}, Score={chem_c * 4 - chem_i}")
            
            return subjects
        except Exception as e:
            print(f"ERROR in subject_wise_analysis: {str(e)}")
            traceback.print_exc()
            return {
                "math": {"correct": 0, "incorrect": 0, "skipped": 0, "score": 0},
                "physics": {"correct": 0, "incorrect": 0, "skipped": 0, "score": 0},
                "chemistry": {"correct": 0, "incorrect": 0, "skipped": 0, "score": 0}
            }
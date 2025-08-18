import gradio as gr
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AirlineAIAssistant:
    def __init__(self):
        # Sample flight data
        self.flights_data = {
            "New York": {
                "Los Angeles": [
                    {"airline": "SkyWings", "departure": "08:00", "price": 299, "duration": "5h 30m"},
                    {"airline": "AeroFly", "departure": "14:30", "price": 329, "duration": "5h 45m"},
                    {"airline": "CloudJet", "departure": "19:15", "price": 279, "duration": "5h 20m"}
                ],
                "Miami": [
                    {"airline": "SunAir", "departure": "06:45", "price": 189, "duration": "3h 15m"},
                    {"airline": "TropicWings", "departure": "16:20", "price": 209, "duration": "3h 05m"}
                ],
                "Chicago": [
                    {"airline": "WindyCity Express", "departure": "10:30", "price": 159, "duration": "2h 45m"},
                    {"airline": "GreatLakes Air", "departure": "18:45", "price": 179, "duration": "2h 30m"}
                ]
            },
            "Los Angeles": {
                "New York": [
                    {"airline": "EastCoast Air", "departure": "07:00", "price": 319, "duration": "5h 15m"},
                    {"airline": "TransContinental", "departure": "12:45", "price": 289, "duration": "5h 25m"}
                ],
                "Seattle": [
                    {"airline": "PacificWings", "departure": "09:15", "price": 149, "duration": "2h 40m"},
                    {"airline": "NorthWest Air", "departure": "15:30", "price": 169, "duration": "2h 50m"}
                ]
            },
            "Miami": {
                "New York": [
                    {"airline": "Atlantic Express", "departure": "11:20", "price": 199, "duration": "3h 10m"},
                    {"airline": "Coastal Air", "departure": "17:40", "price": 219, "duration": "3h 20m"}
                ]
            },
            "Chicago": {
                "New York": [
                    {"airline": "Midwest Express", "departure": "08:30", "price": 169, "duration": "2h 35m"},
                    {"airline": "Central Air", "departure": "14:15", "price": 189, "duration": "2h 40m"}
                ]
            },
            "Seattle": {
                "Los Angeles": [
                    {"airline": "Coast to Coast", "departure": "13:00", "price": 159, "duration": "2h 45m"},
                    {"airline": "Western Wings", "departure": "20:30", "price": 139, "duration": "2h 55m"}
                ]
            }
        }
        
        # Booking storage
        self.bookings = []
        self.booking_counter = 1000
        self.seat_assignments = {}  # flight_key -> list of assigned seats
        
        # Current booking session data
        self.current_session = {
            "source": None,
            "destination": None,
            "selected_flight": None,
            "passenger_name": None,
            "passenger_age": None,
            "step": "start"
        }
    
    def get_available_cities(self) -> List[str]:
        """Get list of all available cities"""
        cities = set(self.flights_data.keys())
        for destination_dict in self.flights_data.values():
            cities.update(destination_dict.keys())
        return sorted(list(cities))
    
    def check_flight_availability(self, source: str, destination: str) -> str:
        """Check available flights between source and destination"""
        if source.lower() == destination.lower():
            return "❌ Error: Source and destination cannot be the same city."
        
        if source in self.flights_data and destination in self.flights_data[source]:
            flights = self.flights_data[source][destination]
            result = f"✈️ **Available flights from {source} to {destination}:**\n\n"
            
            for i, flight in enumerate(flights, 1):
                result += f"**Option {i}:**\n"
                result += f"• Airline: {flight['airline']}\n"
                result += f"• Departure: {flight['departure']}\n"
                result += f"• Duration: {flight['duration']}\n"
                result += f"• Price: ${flight['price']}\n\n"
            
            return result
        else:
            return f"❌ Sorry, no flights available from {source} to {destination}."
    
    def generate_seat_number(self, flight_key: str) -> str:
        """Generate a unique seat number for a flight"""
        if flight_key not in self.seat_assignments:
            self.seat_assignments[flight_key] = []
        
        # Generate seat (rows 1-30, seats A-F)
        while True:
            row = random.randint(1, 30)
            seat_letter = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
            seat = f"{row}{seat_letter}"
            
            if seat not in self.seat_assignments[flight_key]:
                self.seat_assignments[flight_key].append(seat)
                return seat
    
    def create_ticket_file(self, booking_data: Dict) -> str:
        """Create individual ticket file"""
        filename = f"{booking_data['passenger_name'].replace(' ', '_')}_{booking_data['booking_number']}.txt"
        
        ticket_content = f"""
╔══════════════════════════════════════╗
║           AIRLINE TICKET             ║
╚══════════════════════════════════════╝

Booking Number: {booking_data['booking_number']}
Date of Booking: {booking_data['booking_date']}

PASSENGER DETAILS:
Name: {booking_data['passenger_name']}
Age: {booking_data['passenger_age']}

FLIGHT DETAILS:
From: {booking_data['source']}
To: {booking_data['destination']}
Airline: {booking_data['airline']}
Departure Time: {booking_data['departure_time']}
Duration: {booking_data['duration']}
Seat Number: {booking_data['seat_number']}
Price: ${booking_data['price']}

Thank you for choosing our airline!
Have a pleasant journey! ✈️
"""
        
        try:
            with open(filename, 'w') as f:
                f.write(ticket_content)
            return f"✅ Ticket saved as: {filename}"
        except Exception as e:
            return f"❌ Error saving ticket: {str(e)}"
    
    def generate_summary_report(self) -> str:
        """Generate summary report of all bookings"""
        if not self.bookings:
            return "📊 No bookings to summarize yet."
        
        try:
            with open('summary_report.txt', 'w') as f:
                f.write("╔══════════════════════════════════════╗\n")
                f.write("║        AIRLINE BOOKING SUMMARY       ║\n")
                f.write("╚══════════════════════════════════════╝\n\n")
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Bookings: {len(self.bookings)}\n\n")
                
                total_revenue = 0
                for i, booking in enumerate(self.bookings, 1):
                    f.write(f"BOOKING #{i}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Booking Number: {booking['booking_number']}\n")
                    f.write(f"Passenger: {booking['passenger_name']} (Age: {booking['passenger_age']})\n")
                    f.write(f"Route: {booking['source']} → {booking['destination']}\n")
                    f.write(f"Airline: {booking['airline']}\n")
                    f.write(f"Departure: {booking['departure_time']}\n")
                    f.write(f"Duration: {booking['duration']}\n")
                    f.write(f"Seat: {booking['seat_number']}\n")
                    f.write(f"Price: ${booking['price']}\n")
                    f.write(f"Booking Date: {booking['booking_date']}\n\n")
                    total_revenue += booking['price']
                
                f.write("=" * 40 + "\n")
                f.write(f"TOTAL REVENUE: ${total_revenue}\n")
            
            return f"📊 Summary report generated successfully! File: summary_report.txt\n📈 Total bookings: {len(self.bookings)} | Total revenue: ${total_revenue}"
        
        except Exception as e:
            return f"❌ Error generating report: {str(e)}"
    
    def reset_session(self):
        """Reset current booking session"""
        self.current_session = {
            "source": None,
            "destination": None,
            "selected_flight": None,
            "passenger_name": None,
            "passenger_age": None,
            "step": "start"
        }
    
    def process_message(self, message: str) -> str:
        """Main message processing function"""
        message = message.strip().lower()
        
        # Handle different commands and conversation flow
        if any(word in message for word in ["hello", "hi", "hey", "start"]):
            self.reset_session()
            cities = ", ".join(self.get_available_cities())
            return f"🛫 Welcome to Airline AI Assistant! I can help you:\n\n✈️ Check flight availability\n🎫 Book flights step-by-step\n📊 Generate booking reports\n\nAvailable cities: {cities}\n\nHow can I assist you today?"
        
        elif any(word in message for word in ["check", "availability", "flights", "search"]):
            if "from" in message and "to" in message:
                # Try to extract cities from message
                parts = message.split()
                try:
                    from_idx = parts.index("from")
                    to_idx = parts.index("to")
                    if from_idx < to_idx and from_idx + 1 < len(parts) and to_idx + 1 < len(parts):
                        source = parts[from_idx + 1].title()
                        destination = parts[to_idx + 1].title()
                        return self.check_flight_availability(source, destination)
                except (ValueError, IndexError):
                    pass
            
            cities = ", ".join(self.get_available_cities())
            return f"🔍 To check flight availability, please specify:\n'Check flights from [Source City] to [Destination City]'\n\nAvailable cities: {cities}"
        
        elif any(word in message for word in ["book", "booking", "reserve"]):
            if self.current_session["step"] == "start":
                self.current_session["step"] = "get_source"
                cities = ", ".join(self.get_available_cities())
                return f"🎫 Let's book your flight! \n\nStep 1: Which city are you departing from?\nAvailable cities: {cities}"
            else:
                return self.handle_booking_flow(message)
        
        elif any(word in message for word in ["report", "summary"]):
            return self.generate_summary_report()
        
        elif any(word in message for word in ["help", "commands"]):
            return """🤖 **Available Commands:**
            
✈️ **Flight Search:** "Check flights from [City] to [City]"
🎫 **Book Flight:** "Book" or "Book flight"
📊 **Generate Report:** "Generate report" or "Summary"
🔄 **Reset/Start Over:** "Reset" or "Start over"
❓ **Help:** "Help" or "Commands"

**Available Cities:** New York, Los Angeles, Miami, Chicago, Seattle

**Example:** "Check flights from New York to Los Angeles" """
        
        elif any(word in message for word in ["reset", "start over", "cancel"]):
            self.reset_session()
            return "🔄 Session reset! How can I help you today?"
        
        else:
            # Handle booking flow if in progress
            if self.current_session["step"] != "start":
                return self.handle_booking_flow(message)
            else:
                return "🤔 I didn't understand that. Type 'help' to see available commands, or try:\n• 'Check flights from [city] to [city]'\n• 'Book flight'\n• 'Generate report'"
    
    def handle_booking_flow(self, message: str) -> str:
        """Handle the step-by-step booking process"""
        cities = self.get_available_cities()
        
        if self.current_session["step"] == "get_source":
            # Find matching city
            source_city = None
            for city in cities:
                if city.lower() in message.lower():
                    source_city = city
                    break
            
            if source_city:
                self.current_session["source"] = source_city
                self.current_session["step"] = "get_destination"
                available_destinations = [city for city in cities if city != source_city]
                return f"✅ Departure city: {source_city}\n\nStep 2: Which city is your destination?\nAvailable destinations: {', '.join(available_destinations)}"
            else:
                cities_str = ", ".join(cities)
                return f"❌ Please specify a valid departure city from: {cities_str}"
        
        elif self.current_session["step"] == "get_destination":
            destination_city = None
            for city in cities:
                if city.lower() in message.lower():
                    destination_city = city
                    break
            
            if destination_city:
                if destination_city == self.current_session["source"]:
                    return "❌ Destination cannot be the same as departure city. Please choose a different destination."
                
                self.current_session["destination"] = destination_city
                
                # Check if flights exist
                if (self.current_session["source"] in self.flights_data and 
                    destination_city in self.flights_data[self.current_session["source"]]):
                    
                    flights = self.flights_data[self.current_session["source"]][destination_city]
                    self.current_session["step"] = "select_flight"
                    
                    result = f"✅ Route: {self.current_session['source']} → {destination_city}\n\n"
                    result += "✈️ **Available Flights:**\n\n"
                    
                    for i, flight in enumerate(flights, 1):
                        result += f"**Option {i}:** {flight['airline']}\n"
                        result += f"• Departure: {flight['departure']}\n"
                        result += f"• Duration: {flight['duration']}\n"
                        result += f"• Price: ${flight['price']}\n\n"
                    
                    result += "Please select your flight by typing the option number (1, 2, 3, etc.)"
                    return result
                else:
                    self.reset_session()
                    return f"❌ Sorry, no flights available from {self.current_session['source']} to {destination_city}."
            else:
                available_destinations = [city for city in cities if city != self.current_session["source"]]
                return f"❌ Please specify a valid destination from: {', '.join(available_destinations)}"
        
        elif self.current_session["step"] == "select_flight":
            try:
                choice = int(message.strip())
                flights = self.flights_data[self.current_session["source"]][self.current_session["destination"]]
                
                if 1 <= choice <= len(flights):
                    self.current_session["selected_flight"] = flights[choice - 1]
                    self.current_session["step"] = "get_passenger_details"
                    
                    flight = self.current_session["selected_flight"]
                    return f"""✅ **Flight Selected:**
• Airline: {flight['airline']}
• Departure: {flight['departure']}
• Duration: {flight['duration']}
• Price: ${flight['price']}

Step 3: Please provide passenger details in this format:
'Name: [Full Name], Age: [Age]'

Example: 'Name: John Smith, Age: 30'"""
                else:
                    return f"❌ Invalid option. Please select a number between 1 and {len(flights)}."
            except ValueError:
                return "❌ Please enter a valid flight option number (1, 2, 3, etc.)"
        
        elif self.current_session["step"] == "get_passenger_details":
            # Parse passenger details
            try:
                parts = message.split(',')
                name_part = None
                age_part = None
                
                for part in parts:
                    part = part.strip()
                    if part.lower().startswith('name:'):
                        name_part = part[5:].strip()
                    elif part.lower().startswith('age:'):
                        age_part = part[4:].strip()
                
                if name_part and age_part:
                    try:
                        age = int(age_part)
                        if age < 0 or age > 120:
                            return "❌ Please enter a valid age (0-120)."
                        
                        self.current_session["passenger_name"] = name_part
                        self.current_session["passenger_age"] = age
                        
                        # Complete the booking
                        return self.complete_booking()
                    except ValueError:
                        return "❌ Please enter a valid age as a number."
                else:
                    return "❌ Please provide details in the format: 'Name: [Full Name], Age: [Age]'"
            except Exception:
                return "❌ Please provide details in the format: 'Name: [Full Name], Age: [Age]'"
        
        return "🤔 I didn't understand that. Type 'help' for assistance or 'reset' to start over."
    
    def complete_booking(self) -> str:
        """Complete the flight booking process"""
        try:
            # Generate booking number
            booking_number = f"FL{self.booking_counter}"
            self.booking_counter += 1
            
            # Generate seat number
            flight_key = f"{self.current_session['source']}-{self.current_session['destination']}-{self.current_session['selected_flight']['airline']}"
            seat_number = self.generate_seat_number(flight_key)
            
            # Create booking data
            booking_data = {
                "booking_number": booking_number,
                "booking_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "passenger_name": self.current_session["passenger_name"],
                "passenger_age": self.current_session["passenger_age"],
                "source": self.current_session["source"],
                "destination": self.current_session["destination"],
                "airline": self.current_session["selected_flight"]["airline"],
                "departure_time": self.current_session["selected_flight"]["departure"],
                "duration": self.current_session["selected_flight"]["duration"],
                "price": self.current_session["selected_flight"]["price"],
                "seat_number": seat_number
            }
            
            # Save booking
            self.bookings.append(booking_data)
            
            # Create ticket file
            ticket_status = self.create_ticket_file(booking_data)
            
            # Reset session
            self.reset_session()
            
            result = f"""🎉 **Booking Confirmed!**

📋 **Booking Details:**
• Booking Number: {booking_data['booking_number']}
• Passenger: {booking_data['passenger_name']} (Age: {booking_data['passenger_age']})
• Route: {booking_data['source']} → {booking_data['destination']}
• Airline: {booking_data['airline']}
• Departure: {booking_data['departure_time']}
• Duration: {booking_data['duration']}
• Seat: {booking_data['seat_number']}
• Price: ${booking_data['price']}

{ticket_status}

Thank you for booking with us! ✈️
Type 'book' to make another booking or 'report' to see all bookings."""

            return result
            
        except Exception as e:
            self.reset_session()
            return f"❌ Error completing booking: {str(e)}. Please try again."

# Initialize the assistant
assistant = AirlineAIAssistant()

def chatbot_response(message: str, history: List[Tuple[str, str]]) -> str:
    """Process user message and return response"""
    if not message.strip():
        return "Please enter a message."
    
    return assistant.process_message(message)

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Airline AI Assistant", theme=gr.themes.Soft()) as iface:
        gr.HTML("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1>✈️ Airline AI Assistant</h1>
            <p>Your intelligent flight booking companion</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    value=[["Assistant", "🛫 Welcome to Airline AI Assistant! I can help you:\n\n✈️ Check flight availability\n🎫 Book flights step-by-step\n📊 Generate booking reports\n\nType 'help' for commands or start by saying 'book flight' or 'check flights'!"]],
                    height=500,
                    show_label=False
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Type your message here... (e.g., 'check flights from New York to Los Angeles')",
                        show_label=False,
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="padding: 20px; background-color: #f0f9ff; border-radius: 10px; margin-bottom: 10px;">
                    <h3>🗺️ Available Cities</h3>
                    <ul>
                        <li>New York</li>
                        <li>Los Angeles</li>
                        <li>Miami</li>
                        <li>Chicago</li>
                        <li>Seattle</li>
                    </ul>
                </div>
                """)
                
                gr.HTML("""
                <div style="padding: 20px; background-color: #f0fdf4; border-radius: 10px; margin-bottom: 10px;">
                    <h3>💡 Quick Commands</h3>
                    <ul>
                        <li><strong>Search:</strong> "Check flights from [city] to [city]"</li>
                        <li><strong>Book:</strong> "Book flight"</li>
                        <li><strong>Report:</strong> "Generate report"</li>
                        <li><strong>Help:</strong> "Help"</li>
                        <li><strong>Reset:</strong> "Reset"</li>
                    </ul>
                </div>
                """)
                
                # Buttons for quick actions
                with gr.Column():
                    check_btn = gr.Button("🔍 Check Flights", variant="secondary")
                    book_btn = gr.Button("🎫 Book Flight", variant="secondary")
                    report_btn = gr.Button("📊 Generate Report", variant="secondary")
                    help_btn = gr.Button("❓ Help", variant="secondary")
                    reset_btn = gr.Button("🔄 Reset", variant="secondary")
        
        def send_message(message, history):
            if message.strip():
                response = chatbot_response(message, history)
                history.append((message, response))
            return history, ""
        
        def quick_action(action_msg, history):
            response = chatbot_response(action_msg, history)
            history.append((action_msg, response))
            return history
        
        # Event handlers
        send_btn.click(send_message, [msg, chatbot], [chatbot, msg])
        msg.submit(send_message, [msg, chatbot], [chatbot, msg])
        
        check_btn.click(lambda h: quick_action("check flights", h), [chatbot], [chatbot])
        book_btn.click(lambda h: quick_action("book flight", h), [chatbot], [chatbot])
        report_btn.click(lambda h: quick_action("generate report", h), [chatbot], [chatbot])
        help_btn.click(lambda h: quick_action("help", h), [chatbot], [chatbot])
        reset_btn.click(lambda h: quick_action("reset", h), [chatbot], [chatbot])
    
    return iface

# Launch the application
if __name__ == "__main__":
    app = create_interface()
    print("🛫 Starting Airline AI Assistant...")
    print("📋 Features loaded:")
    print("   ✅ Flight availability checking")
    print("   ✅ Step-by-step booking process")
    print("   ✅ Ticket generation")
    print("   ✅ Automated seat assignment")
    print("   ✅ Summary reports")
    print("   ✅ Interactive chat interface")
    print("   ✅ Error handling & validation")
    
    app.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
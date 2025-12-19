import os
import ssl
import certifi
import json

# Set SSL certificate file before importing discord
os.environ['SSL_CERT_FILE'] = certifi.where()

import discord
from discord.ext import commands
import random
import re
import aiohttp
from dotenv import load_dotenv

load_dotenv()
# Configure SSL context to use certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Patch aiohttp ClientSession to use our SSL connector by default
_original_session_init = aiohttp.ClientSession.__init__

def _patched_session_init(self, *args, connector=None, **kwargs):
    if connector is None:
        # Create connector lazily with SSL context
        connector = aiohttp.TCPConnector(ssl=ssl_context, loop=None)
    return _original_session_init(self, *args, connector=connector, **kwargs)

aiohttp.ClientSession.__init__ = _patched_session_init

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)

# JSON file paths for persistence
DATA_DIR = 'data'
QUESTIONS_FILE = os.path.join(DATA_DIR, 'current_questions.json')
ANSWERED_FILE = os.path.join(DATA_DIR, 'question_answered.json')
POINTS_FILE = os.path.join(DATA_DIR, 'user_points.json')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    """Load all data from JSON files"""
    global current_questions, question_answered, user_points
    
    # Load current_questions
    try:
        if os.path.exists(QUESTIONS_FILE):
            with open(QUESTIONS_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to int (channel IDs)
                current_questions = {int(k): v for k, v in data.items()}
        else:
            current_questions = {}
    except Exception as e:
        print(f"Error loading current_questions: {e}")
        current_questions = {}
    
    # Load question_answered
    try:
        if os.path.exists(ANSWERED_FILE):
            with open(ANSWERED_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to int (channel IDs)
                question_answered = {int(k): v for k, v in data.items()}
        else:
            question_answered = {}
    except Exception as e:
        print(f"Error loading question_answered: {e}")
        question_answered = {}
    
    # Load user_points
    try:
        if os.path.exists(POINTS_FILE):
            with open(POINTS_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to int (user IDs)
                user_points = {int(k): v for k, v in data.items()}
        else:
            user_points = {}
    except Exception as e:
        print(f"Error loading user_points: {e}")
        user_points = {}

def save_data():
    """Save all data to JSON files"""
    # Save current_questions
    try:
        # Convert int keys to strings for JSON
        data = {str(k): v for k, v in current_questions.items()}
        with open(QUESTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving current_questions: {e}")
    
    # Save question_answered
    try:
        # Convert int keys to strings for JSON
        data = {str(k): v for k, v in question_answered.items()}
        with open(ANSWERED_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving question_answered: {e}")
    
    # Save user_points
    try:
        # Convert int keys to strings for JSON
        data = {str(k): v for k, v in user_points.items()}
        with open(POINTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving user_points: {e}")

questions = {'keshav': [
    {'q': "KESHAV Multiple Choice: What is Keshav's brother's name?\n"
          "W) Steve\nX) Bob\nY) Sriram\nZ) He refuses to say", 'a': 'Y'},

    {'q': "KESHAV Multiple Choice: Which of the following is Keshav's favorite color?\n"
          "W) Blue\nX) Red\nY) Yellow\nZ) Pink", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav say right before doing absolutely nothing?\n"
          "W) Alright\nX) Bet\nY) One sec\nZ) Let me lock in", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What is Keshav's natural response to confusion?\n"
          "W) Asking questions\nX) Panicking\nY) Nodding confidently\nZ) Running away", 'a': 'Y'},

    {'q': "KESHAV Multiple Choice: What ruins Keshav’s productivity instantly?\n"
          "W) Hunger\nX) Notifications\nY) One minor inconvenience\nZ) Existing", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav open instead of the app he needs?\n"
          "W) Calculator\nX) Notes\nY) Instagram\nZ) Settings", 'a': 'Y'},

    {'q': "KESHAV Multiple Choice: What does Keshav consider 'basically done'?\n"
          "W) 90% complete\nX) 50% complete\nY) Opened once\nZ) Thought about", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What phrase does Keshav use before making things worse?\n"
          "W) Trust me\nX) I got this\nY) It’s fine\nZ) All of the above", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav blame when something goes wrong?\n"
          "W) Himself\nX) The system\nY) Timing\nZ) Vibes", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What would Keshav Google during an exam?\n"
          "W) The answer\nX) How partial credit works\nY) Can confidence replace knowledge\nZ) Am I cooked", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What is Keshav's greatest strength?\n"
          "W) Intelligence\nX) Discipline\nY) Optimism\nZ) Audacity", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav do when running late?\n"
          "W) Hurry\nX) Apologize\nY) Speed up\nZ) Accept fate", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav consider a short break?\n"
          "W) 5 minutes\nX) 15 minutes\nY) 1 hour\nZ) Until tomorrow", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What would Keshav forget first?\n"
          "W) Wallet\nX) Keys\nY) Charger\nZ) His original plan", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What triggers Keshav’s fight-or-flight response?\n"
          "W) Email subject lines\nX) Low battery\nY) 'Can we talk?'\nZ) All of the above", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav do when he hears 'group project'?\n"
          "W) Get excited\nX) Ask questions\nY) Disappear\nZ) Prepare to carry", 'a': 'Y'},

    {'q': "KESHAV Multiple Choice: What does Keshav say when he has zero idea what's happening?\n"
          "W) Yeah\nX) Right\nY) Exactly\nZ) All of the above", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav think fixes everything?\n"
          "W) Sleep\nX) Food\nY) Ignoring it\nZ) Time", 'a': 'Y'},

    {'q': "KESHAV Multiple Choice: What would Keshav overthink the most?\n"
          "W) A text\nX) A look\nY) A tone\nZ) Literally everything", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What is Keshav's relationship with deadlines?\n"
          "W) Respectful\nX) Professional\nY) Negotiable\nZ) Hostile", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav do when plans change?\n"
          "W) Adapt\nX) Ask why\nY) Panic internally\nZ) Pretend it’s fine", 'a': 'Y'},

    {'q': "KESHAV Multiple Choice: What would Keshav bring to a serious meeting?\n"
          "W) Preparation\nX) Confidence\nY) Coffee\nZ) Vibes", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What is Keshav's biggest academic weapon?\n"
          "W) Studying\nX) Practice\nY) Guessing\nZ) Manifestation", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav say after making a mistake?\n"
          "W) Sorry\nX) My bad\nY) Interesting\nZ) That was intentional", 'a': 'Y'},

    {'q': "KESHAV Multiple Choice: What would Keshav procrastinate by doing?\n"
          "W) Cleaning\nX) Organizing files\nY) Planning productivity\nZ) Everything", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav think 'locking in' means?\n"
          "W) Focus\nX) Silence\nY) Sitting upright\nZ) Opening a new tab", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What is Keshav actually doing right now?\n"
          "W) Working\nX) Studying\nY) Relaxing\nZ) Avoiding responsibility", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav fear most?\n"
          "W) Failure\nX) Embarrassment\nY) Awkward silence\nZ) Mild inconvenience", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What is Keshav's life motto?\n"
          "W) Work hard\nX) Stay focused\nY) Be disciplined\nZ) It’ll probably work out", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav do after saying 'last one'?\n"
          "W) Stop\nX) Pause\nY) Think\nZ) Continue indefinitely", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What would Keshav accidentally overcommit to?\n"
          "W) One task\nX) Two tasks\nY) Three tasks\nZ) Everything at once", 'a': 'Z'},

    {'q': "KESHAV Multiple Choice: What does Keshav believe counts as progress?\n"
          "W) Results\nX) Effort\nY) Opening the document\nZ) Thinking about starting", 'a': 'Z'}
],
            'nikhil': [{'q': 'NIKHIL Short Answer: How many questions did Nikhil answer in the 2025 Sandia Labs Regional Science Bowl Competition?', 'a': 'ZERO'}, {'q': 'NIKHIL Multiple Choice: What is Nikhil\'s last name? \n W) Sinner X) Sinna Y) Sinnha Z) Sinha', 'a': 'Z'}],
    'phy': [{'q': 'PHYSICS Multiple Choice: Which of the following thermodynamic properties is a path function?\n'
               'W) Energy\n'
               'X) Enthalpy [EN-thul-pee]\n'
               'Y) Entropy [EN-troh-pee]\n'
               'Z) Work',
          'a': 'Z'},
         {'q': 'PHYSICS Short Answer: A particle has a position defined by the equation x = 3t + 18. What is the '
               'acceleration of the particle at t = 5?',
          'a': 'ZERO'},
         {'q': 'PHYSICS Short Answer: The electric force on a point charge as a result of another charge is given as '
               'M. If the distance between the two particles is halved, what is the new force on the point charge?',
          'a': '4M'},
         {'q': 'PHYSICS Multiple Choice: Which of the following is closest to the amount of energy, in joules [jools], '
               'carried by a mole of photons with a wavelength of one micrometer?\n'
               'W) 12,000\n'
               'X) 24,000\n'
               'Y) 120,000\n'
               'Z) 240,000',
          'a': 'Y'},
         {'q': 'PHYSICS Multiple Choice: Which of the following is not a logical corollary to special relativity?\n'
               'W) Time dilation\n'
               'X) Relativity of simultaneity\n'
               'Y) Curvature of spacetime\n'
               'Z) Length contraction',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: What effect describes the inelastic scattering of photons by free charged '
               'particles?',
          'a': 'COMPTON EFFECT'},
         {'q': 'PHYSICS Short Answer: The maximal increase in the velocity of an ideal rocket is linearly proportional '
               'to what property of the rocket?',
          'a': 'EXHAUST VELOCITY'},
         {'q': 'PHYSICS Short Answer: Bill’s weight on a theoretical perfectly spherical Earth is 700 newtons. If Bill '
               'stood on the surface of a planet with the same mass and radius as Earth, but that was shaped as a '
               'hollow sphere with thickness 60 kilometers, what is Bill’s new weight, in newtons to one significant '
               'figure?',
          'a': '700'},
         {'q': 'PHYSICS Multiple Choice: Which of the following thermodynamic properties is not a state function?\n'
               'W) Energy\n'
               'X) Enthalpy [EN-thul-pee]\n'
               'Y) Heat\n'
               'Z) Entropy [EN-troh-pee]',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: What principle in physics states that pressure changes on an incompressible, '
               'enclosed, static fluid are evenly distributed?',
          'a': "PASCAL'S LAW"},
         {'q': 'PHYSICS Short Answer: Given a graph with acceleration on the y-axis and time on the x-axis, what '
               'physical quantity does the area under the curve represent?',
          'a': 'VELOCITY'},
         {'q': 'PHYSICS Multiple Choice: If one left-circularly polarized laser beam and one right-circularly '
               'polarized laser beam with the same amplitude and frequency are combined into a single beam, what is '
               'the polarization of the resulting beam?\n'
               'W) Circular\n'
               'X) Elliptical\n'
               'Y) Linear\n'
               'Z) Unpolarized',
          'a': 'Y'},
         {'q': 'PHYSICS Multiple Choice: A 10,000-kilogram truck is rolling at 2 meters per second when 5000 kilograms '
               "of cargo is dropped into it. Which of the following, in meters per second, is closest to the truck's "
               'speed afterwards?\n'
               'W) 1\n'
               'X) 1.3\n'
               'Y) 1.5\n'
               'Z) 2',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: Identify all of the following three statements that are true of light: 1) '
               'Diffraction is an example of the wave-nature of light; 2) Interference is an example of the '
               'wave-nature of light; 3) The energy carried by light is directly proportional to frequency.',
          'a': 'ALL'},
         {'q': 'PHYSICS Short Answer: In a viscous fluid, what is the type of flow characterized by having layers of '
               'currents that are all parallel to the flow?',
          'a': 'LAMINAR'},
         {'q': 'PHYSICS Short Answer: An ideal pendulum has a period of 1 second. If its mass is multiplied by 3 and '
               'its length is multiplied by 4, in seconds, what is the new period of the pendulum?',
          'a': '2'},
         {'q': 'PHYSICS Multiple Choice: If a constant force is applied to an object, which of the following '
               'quantities must also be constant?\n'
               'W) Position\n'
               'X) Acceleration\n'
               'Y) Velocity\n'
               'Z) Speed',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: A Carnot engine is operating between a hot reservoir at 125 degrees Celsius and '
               'a cold reservoir at 25 degrees Celsius. If the engine extracts 600 joules [jools] from the hot '
               'reservoir, to two significant figures and in joules [jools], how much heat is discarded as waste per '
               'cycle?',
          'a': '450'},
         {'q': 'PHYSICS Short Answer: A circuit contains a 6-volt battery and a 2-ohm resistor. What is the power, in '
               'watts, of this circuit?',
          'a': '18'},
         {'q': 'PHYSICS Multiple Choice: If an electron in a hydrogen atom decays to emit a photon, which of the '
               'following transitions emits the longest wavelength photon?\n'
               'W) First excited state to ground state\n'
               'X) Second excited state to ground state\n'
               'Y) Second excited state to first excited state\n'
               'Z) Third excited state to first excited state',
          'a': 'Y'},
         {'q': 'PHYSICS Multiple Choice: For which of the following is Erwin Schrodinger most famous?\n'
               'W) Describing how wavefunctions change over time\n'
               'X) Discovering that electrons occupy energy levels in atoms\n'
               'Y) Discovering that atoms contain a positively charged nucleus\n'
               'Z) Discovering nuclear fission',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: Identify all of the following three statements that are true of semiconductors: '
               '1) Silicon dioxide is a semiconductor; 2) Silicon is commonly used as a semiconductor; 3) LEDs can be '
               'made of semiconductors.',
          'a': '2 AND 3'},
         {'q': 'PHYSICS Short Answer: A hydraulic press has two ends that are level but have different areas. Identify '
               'all of the following 4 quantities that may have differing magnitudes at the two ends: 1) Force; 2) '
               'Work; 3) Displacement;\n'
               '4) Pressure.',
          'a': '1 AND 3'},
         {'q': 'PHYSICS Short Answer: Identify all of the following 3 classes of levers that are capable of producing '
               'a mechanical advantage greater than unity: 1) Class 1; 2) Class 2; 3) Class 3.',
          'a': '1 AND 2'},
         {'q': 'PHYSICS Multiple Choice: Uniform circular motion is achieved by applying force in what direction?\n'
               'W) Toward the center of rotation\n'
               'X) Away from the center of rotation\n'
               'Y) In the direction of motion\n'
               'Z) Against the direction of motion',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: What radioactive isotope of carbon is prominently used in radiometric dating?',
          'a': 'CARBON-14'},
         {'q': 'PHYSICS Short Answer: On a standing wave, what term refers to the points at which the amplitude is '
               'maximized?',
          'a': 'ANTI-NODE'},
         {'q': 'PHYSICS Short Answer: Suppose the Earth’s radius were decreased by half but its mass remained the '
               'same. To one decimal place, by what factor will the surface escape velocity be multiplied?',
          'a': '1.4'},
         {'q': 'PHYSICS Multiple Choice: What thermodynamic cycle describes a jet turbine?\n'
               'W) Rankine\n'
               'X) Carnot\n'
               'Y) Brayton\n'
               'Z) Otto',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: Identify all of the following three statements that are true of the physics of '
               'the Big Bang:\n'
               '1) The Big Bang is consistent with the observations made by Hubble; 2) The Big Bang produced mostly '
               'oxygen and carbon; 3) The leftover energy from the Big Bang is no longer detectable.',
          'a': '1'},
         {'q': 'PHYSICS Short Answer: What is the term for the quasiparticles present in p-type semiconductors that '
               'represent the absence of electrons?',
          'a': 'HOLES'},
         {'q': 'PHYSICS Short Answer: What is the wavelength, as a fraction of the length of the box, of the third '
               'excited state of a one-particle one-dimensional particle in a box?',
          'a': '1/2'},
         {'q': 'PHYSICS Short Answer: Two billiard balls of equal mass are travelling collinearly in opposite '
               'directions. One has a velocity of 5 meters per second, the other has a velocity of 3 meters per '
               'second. They collide completely inelastically. In meters per second, what is their final speed?',
          'a': 'ONE'},
         {'q': 'PHYSICS Short Answer: A 3-volt battery is connected to two 4-ohm resistors that are connected in '
               'parallel. What is the power, in watts, dissipated by this circuit?',
          'a': '4.5'},
         {'q': 'PHYSICS Short Answer: Most room-temperature permanent magnets are magnets due to what phenomenon that '
               'is commonly seen in iron, nickel, and cobalt?',
          'a': 'FERROMAGNETISM'},
         {'q': 'PHYSICS Short Answer: An atom of uranium-235 at rest undergoes spontaneous nuclear fission to form '
               'krypton-94 and barium-141. If the barium atom moves away at 4 kilometers per second, what is the '
               'speed, to the nearest kilometer per second, of the krypton atom?',
          'a': '6'},
         {'q': 'PHYSICS Multiple Choice: Capillary action refers to which of the following?\n'
               'W) The tendency for objects to flee the center of circular motion\n'
               'X) The change in frequency of a wave depending on the relative motion of the source\n'
               'Y) The property by which liquids can flow against gravity\n'
               'Z) The tendency for fluids to dissipate energy as heat',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: What is the name of the law of electromagnetism that states that the force '
               'exerted on each other by two charged particles is inversely proportional to the square of the distance '
               'between them?',
          'a': "COULOMB'S LAW"},
         {'q': 'PHYSICS Short Answer: A 1000-kilogram car traveling at 15 meters per second takes a turn on a flat '
               'surface with a radius of 50 meters. In kilo-newtons, what is the force of friction on the car?',
          'a': '4.5'},
         {'q': 'PHYSICS Short Answer: A 50-kilogram superhero is standing on a frictionless surface. He fires a '
               '100-gram arrow horizontally at a speed of 200 meters per second at a target. In meters per second, '
               'what is his speed afterwards?',
          'a': '0.4'},
         {'q': 'PHYSICS Short Answer: A proton is traveling counterclockwise in a circle in the x = 0 plane. In what '
               'direction is its magnetic field vector?',
          'a': 'POSITIVE X'},
         {'q': 'PHYSICS Short Answer: What is the adjective for the type of materials that will create an induced '
               'magnetic field opposite to an externally applied magnetic field?',
          'a': 'DIAMAGNETIC'},
         {'q': 'PHYSICS Short Answer: What type of circuits, which include types such as high-pass and low-pass '
               'filters, are composed of a resistor and a capacitor?',
          'a': 'RC CIRCUIT'},
         {'q': 'PHYSICS Short Answer: An object’s position x as a function of time t is: x of t equals t cubed minus t '
               'squared plus 3t plus 5. What is the object’s acceleration at time 2?',
          'a': '10'},
         {'q': 'PHYSICS Multiple Choice: A mass on a spring oscillates at a frequency of 200 hertz, creating a '
               'low-pitch sound.\n'
               'Which of the following can be done to increase the frequency of the sound produced?\n'
               'W) Increase the mass\n'
               'X) Use a stiffer spring\n'
               'Y) Approach the mass-spring system at a high speed\n'
               'Z) Remove the air in the room',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: Identify all of the following three particles that are leptons:\n'
               '1) Neutrino; 2) Gluon; 3) Positron.',
          'a': '1 AND 3'},
         {'q': 'PHYSICS Short Answer: An engine does 15 joules of work while exhausting 35 joules of waste heat. What '
               'is the percent efficiency of the engine?',
          'a': '30'},
         {'q': 'PHYSICS Short Answer: In classical mechanics, impulse can be calculated by finding the area under the '
               'curve on a graph of force versus what quantity?',
          'a': 'TIME'},
         {'q': 'PHYSICS Short Answer: What is the largest resonant wavelength, in meters, for sound waves in a 1-meter '
               'tube that is closed on one end?',
          'a': '4'},
         {'q': 'PHYSICS Multiple Choice: The global positioning system uses corrections to account for special and '
               'general relativistic effects. Which of the following is closest to the daily positional deviation that '
               'would result if these corrections were not accounted for?\n'
               'W) 1 centimeter\n'
               'X) 1 meter\n'
               'Y) 100 meters\n'
               'Z) 10 kilometers',
          'a': 'Z'},
         {'q': 'PHYSICS Multiple Choice: Which of the following correctly describes a magnifying glass?\n'
               'W) Single convex lens\n'
               'X) Two convex lenses\n'
               'Y) Single concave lens\n'
               'Z) Two concave lenses',
          'a': 'W'},
         {'q': 'PHYSICS Multiple Choice: A bicyclist goes over the top of a hill with a radius of 50 meters. Which of '
               'the following is closest to the maximum speed, in meters per second, the cyclist can have without '
               'leaving the ground at the top of the hill?\n'
               'W) 11\n'
               'X) 22\n'
               'Y) 33\n'
               'Z) 44',
          'a': 'X'},
         {'q': 'PHYSICS Multiple Choice: Which of the following are proper units for entropy [EN-troh-pee]?\n'
               'W) Joules [jools]\n'
               'X) Kelvins per joule\n'
               'Y) Joules per kelvin\n'
               'Z) Joule-kelvins',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: An observer is moving at 50 meters per second towards a stationary source that '
               'is emitting a wave with velocity 100 meters per second. What is the ratio of the observed frequency to '
               'the transmitted frequency before the observer passes the source?',
          'a': '3/2'},
         {'q': 'PHYSICS Short Answer: What is the mechanical advantage of a 3.5-foot lever if the fulcrum is located 6 '
               'inches from one end?',
          'a': 'SIX'},
         {'q': 'PHYSICS Short Answer: A piano string is tuned to A440. To two significant figures and in milliseconds, '
               'what is the period of vibration of this string?',
          'a': '2.3'},
         {'q': 'PHYSICS Short Answer: For a particle in an infinite square potential well, how many nodes exist in the '
               'wavefunction within the well, not including the walls, in the third excited state?',
          'a': '3'},
         {'q': 'PHYSICS Multiple Choice: The external presence of which of the following would result in the forward '
               'bias of a p-n junction?\n'
               'W) Electric field directed toward the p region\n'
               'X) Electric field directed toward the n region\n'
               'Y) Magnetic field directed toward the p region\n'
               'Z) Magnetic field directed toward the n region',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: Identify all of the following three statements that could be true of a particle '
               'undergoing constant acceleration: 1) Zero instantaneous velocity; 2) Quadratic increase in velocity; '
               '3) Quadratic increase in position.',
          'a': '1 AND 3'},
         {'q': 'PHYSICS Multiple Choice: Which of the following elements is useful as an isotope label due to the two '
               'most common isotopes having 1 to 1 relative abundance?\n'
               'W) Hydrogen\n'
               'X) Chlorine\n'
               'Y) Bromine [BROH-meen]\n'
               'Z) Iodine',
          'a': 'Y'},
         {'q': 'PHYSICS Multiple Choice: Which of the following laws is NOT always true in electrical circuits?\n'
               "W) Ohm's Law\n"
               "X) Coulomb's Law\n"
               "Y) Kirchoff's 1st Law\n"
               "Z) Faraday's Law of Induction",
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: Three resistors are in parallel and have resistances of X, X, and 200 ohms. The '
               'equivalent resistance of the circuit is 75 ohms. What is the value of X, in ohms?',
          'a': '240'},
         {'q': 'PHYSICS Short Answer: A car brakes to a stop over 15 meters, applying a constant force of 800 newtons '
               'to the car.\n'
               'In joules, what was the initial kinetic energy of the car?',
          'a': '12,000'},
         {'q': 'PHYSICS Short Answer: A block attached to a spring is experiencing simple harmonic motion with a '
               'period of 4.0 seconds. What would the period be, in seconds to two significant figures, if the mass of '
               'the block was halved?',
          'a': '2.8'},
         {'q': 'PHYSICS Short Answer: In classical optics, diffraction is a phenomenon that can be described as '
               'intereference according to what principle?',
          'a': "HUYGEN'S PRINCIPLE"},
         {'q': 'PHYSICS Short Answer: What rule states that if an energy level contains several degenerate orbitals, '
               'the orbitals must all be singly filled before any of them can be doubly filled?',
          'a': "HUND'S RULE"},
         {'q': 'PHYSICS Short Answer: What dimensionless physical constant is equal to the square of the ratio of the '
               'charge of the electron to the Planck charge?',
          'a': 'FINE STRUCTURE CONSTANT'},
         {'q': 'PHYSICS Short Answer: A cyclist is decelerating at 2.5 meters per second squared. If at point A, she '
               'is traveling at 8 meters per second and at point B, she is traveling at 5 meters per second, how long, '
               'in seconds, did it take her to travel from point A to B?',
          'a': '1.2'},
         {'q': 'PHYSICS Short Answer: An ideal ammeter is connected to a 1.5-volt battery and it reads 2 amps. How '
               'much power, in watts, is dissipated by the internal resistence of the battery?',
          'a': '3'},
         {'q': 'PHYSICS Short Answer: How much more power does a 40-decibel sound deliver than a 20-decibel sound?',
          'a': '100'},
         {'q': 'PHYSICS Multiple Choice: Which of the following circuits with two components will behave as an '
               'electrical resonator?\n'
               'W) resistor and capacitor\n'
               'X) resistor and inductor\n'
               'Y) capacitor and inductor\n'
               'Z) capacitor and capacitor',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: The temperature is 27 degrees Celsius outdoors and 17 degrees Celsius indoors. '
               'To the nearest whole number, what is the maximal coefficient of performance that could be attained by '
               'an ideal air conditioner?',
          'a': '30'},
         {'q': 'PHYSICS Short Answer: A car is traveling around a circular track in uniform circular motion. Identify '
               'all of the following three quantities that are constant for the car: 1) Angular velocity; 2) '
               'Acceleration; 3) Radial velocity.',
          'a': '1'},
         {'q': 'PHYSICS Short Answer: What is the name of the principle that states that the lowest energy orbitals of '
               'an atom are filled before higher energy ones?',
          'a': 'AUFBAU PRINCIPLE'},
         {'q': 'PHYSICS Multiple Choice: A swinging door is opened to +80 degrees, and released. It swings to -40 '
               'degrees, then back to +20 degrees and so on before eventually reaching rest at 0 degrees. This '
               'oscillatory behavior can be best described as which of the following?\n'
               'W) Underdamped\n'
               'X) Critically damped\n'
               'Y) Overdamped\n'
               'Z) Undamped',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: Protons and neutrons are made up of what two quarks?', 'a': 'UP AND DOWN'},
         {'q': 'PHYSICS Short Answer: What compound of uranium in the uranium fuel cycle is polyfluorinated '
               '[polly-FLOOR-in-ated] and gaseous?',
          'a': 'UF6'},
         {'q': 'PHYSICS Short Answer: A square conducting loop that has sides of length 10 centimeters is pulled out '
               'of a 5-tesla magnetic field at 1 meter per second. What is the magnitude of the induced EMF, in volts, '
               'in the loop while it is leaving the magnetic field?',
          'a': '0.5'},
         {'q': 'PHYSICS Short Answer: How many vibrational degrees of freedom does a linear triatomic gas molecule '
               'possess?',
          'a': 'FOUR'},
         {'q': 'PHYSICS Short Answer: For an ideal gas, identify all of the following 3 properties that, when '
               'increased alone, would increase the mean free path of a gas molecule: 1) Pressure; 2) Temperature; 3) '
               'Collision area.',
          'a': '2'},
         {'q': 'PHYSICS Short Answer: Identify all of the following 3 changes that would increase the magnetic field '
               'outside an ideal solenoid of infinite length: 1) Increasing current strength; 2) Increasing turn '
               'density; 3) Adding an iron core.',
          'a': 'NONE'},
         {'q': 'PHYSICS Short Answer: What mineral is commonly used in watch crystals and radio transmitters due to '
               'its piezoelectric properties?',
          'a': 'QUARTZ'},
         {'q': 'PHYSICS Short Answer: Modulo a dimensionless constant, the Heisenberg uncertainty principle relates '
               'the products of momentum and positional uncertainties to what constant?',
          'a': 'PLANCK’S CONSTANT'},
         {'q': 'PHYSICS Short Answer: In the Grand Unified Theory, which of its three unified forces separates from '
               'the other two earliest on?',
          'a': 'STRONG'},
         {'q': 'PHYSICS Multiple Choice: In inductors, the back EMF generated most directly depends on which of the '
               'following properties of the circuit?\n'
               'W) Voltage\n'
               'X) Time derivative of voltage\n'
               'Y) Current\n'
               'Z) Time derivative of current',
          'a': 'Z'},
         {'q': 'PHYSICS Short Answer: In an electromagnetic motor, what conductive component generates an '
               'electromotive force?',
          'a': 'ARMATURE'},
         {'q': 'PHYSICS Short Answer: What is the name for the device Michelson and Morley used to disprove the '
               'existence of luminiferous aether?',
          'a': 'INTERFEROMETER'},
         {'q': 'PHYSICS Short Answer: A hydrogen atom is in its 4th excited state. What is the value of its principal '
               'quantum number n?',
          'a': '5'},
         {'q': 'PHYSICS Short Answer: A Wheatstone Bridge is used to measure what property of electrical circuit '
               'components?',
          'a': 'RESISTANCE'},
         {'q': 'PHYSICS Short Answer: Using the harmonic oscillator model, and assuming the force constant is '
               'unchanged between the two molecules, what is the ratio of the fundamental vibrational frequency of '
               'hydrogen to that of deuterium?',
          'a': '√2'},
         {'q': 'PHYSICS Multiple Choice: The photoelectric effect reveals what property of photons?\n'
               'W) Wave-like nature\n'
               'X) Particle-like nature\n'
               'Y) Wave-particle duality\n'
               'Z) Masslessness',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: In quantum mechanics, the operator for momentum is represented by a derivative '
               'with respect to what quantity?',
          'a': 'POSITION'},
         {'q': 'PHYSICS Multiple Choice: A 70-kilogram student is walking at 1 meter per second. Which of the '
               'following is closest to her de Broglie wavelength, in meters?\n'
               'W) 10-34\n'
               'X) 10-35\n'
               'Y) 10-36\n'
               'Z) 10-37',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: Einstein won the Nobel Prize in Physics for his description of what phenomenon?',
          'a': 'PHOTOELECTRIC EFFECT'},
         {'q': 'PHYSICS Short Answer: If the ratio of the lengths of two pendulums is 1:4, what is the ratio of the '
               'frequency of the longer to that of the shorter?',
          'a': '1:2'},
         {'q': 'PHYSICS Short Answer: Radiation from a hypothetical blue dwarf is peaked at a wavelength of 250 '
               'nanometers. A spaceship travelling away from the star at 0.6c observes a spectrum peaked at what '
               'wavelength, in nanometers?',
          'a': '500'},
         {'q': 'PHYSICS Short Answer: If the radial dependence of the electric field of a monopole is 1/r2, what is '
               'the long range radial dependence of an electric dipole?',
          'a': '1/r3'},
         {'q': 'PHYSICS Short Answer: A weight is sinking in a fluid. The drag force on the weight is equal to a '
               'constant times its velocity squared times the density of the fluid. In SI base units, give the '
               'dimensions of the constant.',
          'a': 'METERS SQUARED'},
         {'q': 'PHYSICS Short Answer: Compton scattering is the scattering of X-ray photons from what particle?',
          'a': 'ELECTRON'},
         {'q': 'PHYSICS Multiple Choice: Which of the following is closest to the half-life of a free neutron?\n'
               'W) 1 second\n'
               'X) 10 minutes\n'
               'Y) 100 hours\n'
               'Z) 1000 years',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: By what phenomenon can materials emit electrons in response to incident light?',
          'a': 'PHOTOELECTRIC EFFECT'},
         {'q': 'PHYSICS Short Answer: CPT symmetry is a fundamental concept of nuclear science and theoretical '
               'physics. What do the C, P, and T stand for?',
          'a': 'CHARGE CONJUGATION'},
         {'q': 'PHYSICS Short Answer: Identify all of the following three particles that, according to the standard '
               'model, can be affected by gravity: 1) Electron; 2) Pion; 3) Gluon.',
          'a': '1 AND 2'},
         {'q': 'PHYSICS Short Answer: In fluorescence microscopy, energy from absorbed photons is re-emitted as new '
               'photons. If the new photons have only two-thirds of the momentum of the absorbed photons, what is the '
               'ratio of the wavelength of the new photons to that of the absorbed photons?',
          'a': '1.5'},
         {'q': "PHYSICS Short Answer: Kirchhoff's loop rule is a consequence of what conservation principle?",
          'a': 'CONSERVATION OF ENERGY'},
         {'q': 'PHYSICS Short Answer: A spacecraft approaches Jupiter head-on for a gravitational slingshot maneuver. '
               'Jupiter has an orbital velocity of 13 kilometers per second. If the spacecraft was originally moving '
               'at 20 kilometers per second, what is the maximal final speed, in kilometers per second, it can attain?',
          'a': '46'},
         {'q': 'PHYSICS Short Answer: What is the minimum number of photons created in an electron-positron '
               'annihilation in free space?',
          'a': '2'},
         {'q': 'PHYSICS Short Answer: Because of observed neutrino oscillation, what property of the neutrino must be '
               'non-zero?',
          'a': 'MASS'},
         {'q': 'PHYSICS Short Answer: In an RLC circuit, the resonance frequency is defined to be at the point at '
               'which what quantity is minimized?',
          'a': 'IMPEDENCE'},
         {'q': 'PHYSICS Short Answer: A 50-centimeter-long wire with mass 10 grams is suspended horizontally from a '
               'ceiling, parallel to the x-axis. There is a uniform 1-tesla magnetic field oriented in the y '
               'direction. Assuming gravity is 10 meters per second squared, what is the magnitude of the current, in '
               'amperes to the nearest tenth, that the wire must carry in order to experience no net force?',
          'a': '0.2'},
         {'q': 'PHYSICS Short Answer: Charged-coupled devices and complementary metal oxide sensors are devices '
               'typically used to detect what?',
          'a': 'LIGHT'},
         {'q': 'PHYSICS Multiple Choice: The resulting kinetic energy of an ejected photo-electron is NOT determined '
               'by which of the following?\n'
               'W) Speed of light\n'
               'X) Energy of light\n'
               'Y) Work function of the metal\n'
               'Z) Light intensity',
          'a': 'Z'},
         {'q': 'PHYSICS Short Answer: What is the name of the low-temperature state characterized by zero resistance '
               'transport of electron pairs?',
          'a': 'SUPERCONDUCTIVITY'},
         {'q': 'PHYSICS Short Answer: Most ships are more stable in a capsized rather than upright state. Order the '
               'following points from bottom-most to top-most for an upright, metastable ship: 1) Center of gravity; '
               '2) Center of buoyancy; 3) Metacenter.',
          'a': '2, 1, 3'},
         {'q': 'PHYSICS Short Answer: How much work, in joules [jools], is done on a particle of charge 2 coulombs as '
               'it accelerates over a distance of 1 meter in an electric field of strength 9 volts per meter?',
          'a': '18'},
         {'q': "PHYSICS Multiple Choice: Which of the following conservation laws is related by Noether's theorem to "
               'translational spatial symmetry?\n'
               'W) Conservation of mass\n'
               'X) Conservation of linear momentum\n'
               'Y) Conservation of angular momentum\n'
               'Z) Conservation of electric charge',
          'a': 'X'},
         {'q': "PHYSICS Short Answer: The precession of Mercury's orbit about the sun presented an anomaly for the "
               'scientists that observed it. What theory correctly predicted the magnitude of precession each year?',
          'a': 'GENERAL RELATIVITY'},
         {'q': 'PHYSICS Short Answer: A charged conducting sphere is connected by a long, thin conducting wire to an '
               'uncharged conducting sphere that has half the radius of the first sphere. After some time has passed, '
               'what fraction of the original charge remains on the first sphere?',
          'a': '2/3'},
         {'q': 'PHYSICS Short Answer: What quark was most recently discovered?', 'a': 'TOP QUARK'},
         {'q': 'PHYSICS Short Answer: If an electron is moving in the positive-x direction with increasing speed, '
               'identify all of the following three scenarios that could be responsible for the driving force: 1) A '
               'magnetic field pointing in the negative-x direction; 2) An electric field pointing in the negative-x '
               'direction; 3) A magnetic field pointing in the negative-z direction.',
          'a': '2'}, {'q': 'PHYSICS Short Answer: Planck was able to describe the color change of black bodies at different '
               'temperatures by introducing what concept?',
          'a': 'QUANTUM'},
         {'q': 'PHYSICS Short Answer: A horizontal force of 90 newtons is applied to a 20-kilogram block that is '
               'initially at rest on a horizontal surface. The coefficient of static friction between the block and '
               'the surface is 0.5 and the coefficient of kinetic friction of 0.2. In meters per second squared, what '
               'is the acceleration of the block?',
          'a': '0'},
         {'q': 'PHYSICS Multiple Choice: Which of the following is NOT true of laser light?\n'
               'W) It is highly coherent\n'
               'X) It is highly dispersive\n'
               'Y) It is highly monochromatic\n'
               'Z) It is highly directional',
          'a': 'X'},
         {'q': 'PHYSICS Multiple Choice: What type of image is produced by a concave spherical mirror when an object '
               'is placed outside its focal point?\n'
               'W) Real and upright\n'
               'X) Real and inverted\n'
               'Y) Virtual and upright\n'
               'Z) Virtual and inverted',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: A helicopter uses a main rotor as propulsion and control, but requires a tail '
               'rotor to counteract torque. The balance of forces resulting from this configuration is represented '
               "best by which of Newton's laws?",
          'a': 'THIRD'},
         {'q': 'PHYSICS Short Answer: Measured in radians per second, what is the resonant angular frequency of a '
               'circuit consisting of a 2 millifarad capacitor and an 8 millihenry inductor?',
          'a': '250'},
         {'q': 'PHYSICS Multiple Choice: Which of the following isotopes is fissile?\n'
               'W) Thorium-232\n'
               'X) Uranium-233\n'
               'Y) Uranium-238\n'
               'Z) Plutonium-238',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: Two resistors in parallel have an equivalent resistance of 6 ohms.\n'
               'One of the resistors has a resistance of 8 ohms. What is the resistance, in ohms, of the second '
               'resistor?',
          'a': '24'},
         {'q': 'PHYSICS Short Answer: What principle states that the net response at a given point caused by two waves '
               'is the sum of the responses that those waves would have caused individually?',
          'a': 'SUPERPOSITION'},
         {'q': 'PHYSICS Short Answer: What is the term for the useful work that can be obtainable from a closed system '
               'at constant temperature?',
          'a': 'HELMHOLTZ FREE ENERGY'},
         {'q': 'PHYSICS Short Answer: For an airplane in steady, level flight, what resisting force is equal and '
               'opposite to the vehicle thrust?',
          'a': 'DRAG'},
         {'q': 'PHYSICS Short Answer: To the nearest microfarad, what is the capacitance of a standard parallel plate '
               'capacitor with plate separation of 1 micron and plate area of 1 meter squared?',
          'a': '9'},
         {'q': 'PHYSICS Short Answer: What electronic measuring instrument may be used as an ohmmeter, ammeter, or '
               'voltmeter?',
          'a': 'MULTIMETER'},
         {'q': 'PHYSICS Short Answer: To the nearest whole number of joules, what is the work done by gravity on a '
               '500-gram ball that has rolled 20 meters down a 30-degree incline?',
          'a': '49'},
         {'q': 'PHYSICS Short Answer: A Carnot engine operates between a hot temperature of 527 degrees Celsius and a '
               'cold temperature of 127 degrees Celsius. What is its efficiency?',
          'a': '50%'},
         {'q': 'PHYSICS Short Answer: Three resistors are connected in parallel to a 10-amp DC current source. If the '
               'individual resistances are 5 ohms, 8 ohms and 20 ohms, what is the power, to the nearest watt, '
               'dissipated by the circuit?',
          'a': '267'},
         {'q': 'PHYSICS Multiple Choice: In millimeters, what must the focal length of the objective lens of a '
               'telescope be in order to produce a magnification of 300 when used with a 3-millimeter eye piece?\n'
               'W) 100\n'
               'X) 300\n'
               'Y) 900\n'
               'Z) 1200',
          'a': 'Y'},
         {'q': "PHYSICS Short Answer: What technique uses Bragg's law to identify and characterize crystal structures?",
          'a': 'DIFFRACTION'},
         {'q': 'PHYSICS Multiple Choice: Which of the following circuit elements resists instantaneous changes in the '
               'voltage applied to it?\n'
               'W) Inductor\n'
               'X) Capacitor\n'
               'Y) Resistor\n'
               'Z) Transformer',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: If a helicopter loses engine power at a sufficient height and speed, it is able '
               'to autorotate to the ground, extracting energy from the air and, sometimes, landing safely. In this '
               'case, gravitational potential energy is converted into what type of energy?',
          'a': 'MECHANICAL'},
         {'q': 'PHYSICS Short Answer: A ball is thrown at a 30 degree angle with respect to the horizontal at a speed '
               'of 60 meters per second. At what time, to the nearest whole second, does the ball reach the highest '
               'point in its trajectory?',
          'a': '3'},
         {'q': 'PHYSICS Multiple Choice: Given that it relates the energy of a photon to its frequency, what are the '
               "SI units of Planck's constant?\n"
               'W) Joule seconds\n'
               'X) Watts\n'
               'Y) Newton meters\n'
               'Z) Watts per second',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: Carbon-10 has a half-life of approximately 19 seconds.\n'
               'Approximately how long, in seconds, will it take for a sample of carbon-10 to decay to one- sixteenth '
               'of its original size?',
          'a': '76'},
         {'q': 'PHYSICS Multiple Choice: Which of the following dictates that the maximum percentage of power that can '
               'be extracted from a p-n junction solar cell is 33.7%?\n'
               "W) Biot Savart's Law\n"
               "X) Ampere's Law\n"
               'Y) Shockley - Queisser [KYE-zur] Limit\n'
               "Z) Betz's Law",
          'a': 'Y'},
         {'q': "PHYSICS Multiple Choice: A rock on the end of a string is being swung in a circle above a child's "
               'head. The string breaks. Neglecting gravity, in what direction does the acceleration of the rock now '
               'point?\n'
               'W) Tangent to the circle\n'
               'X) Inwards towards the center of the circle\n'
               'Y) Outwards away from the center of the circle\n'
               'Z) The acceleration is now zero',
          'a': 'Z'},
         {'q': 'PHYSICS Short Answer: What is the most malleable element at STP?', 'a': 'GOLD'},
         {'q': 'PHYSICS Multiple Choice: Light traveling in a vacuum hits a refractive material at an angle of\n'
               '60 degrees from the normal. If it travels through the material at an angle of 30 degrees from the '
               'normal, which of the following is the refractive index of the material?\n'
               'W) Square root of 3 divided by 2\n'
               'X) Square root of 3\n'
               'Y) 2\n'
               'Z) 2 times the square root of 2',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: How many lumens does an isotropic source of 1 candela emit into the upper half '
               'plane?',
          'a': '2π'},
         {'q': 'PHYSICS Multiple Choice: Which of the following is the equivalent resistance, in ohms, of a circuit in '
               'which a 5 ohm resistor is connected in series to two 4 ohm resistors which are connected in parallel?\n'
               'W) 10/7\n'
               'X) 40/13\n'
               'Y) 7\n'
               'Z) 13',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: A man drops a 10 kilogram rock from the top of a building of height\n'
               '180 meters. If you assume the acceleration due to gravity is 10 meters per second squared, what is the '
               'speed, in meters per second, of the rock just before it hits the ground?',
          'a': '60'},
         {'q': 'PHYSICS Multiple Choice: A student at the edge of a merry-go-round travels along an arc of length 6.28 '
               'meters as the ride completes a pi/4 angular rotation. To the nearest meter, what is the radius of the '
               'ride?\n'
               'W) 2\n'
               'X) 4\n'
               'Y) 8\n'
               'Z) 16',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: An object is placed 10 centimeters from a thin lens with a focal length of 2 '
               'centimeters. With a negative sign meaning an inverted image, what is the magnification of this system?',
          'a': '-1/4'},
         {'q': 'PHYSICS Multiple Choice: What is the arc length, in miles, traveled by a rocket along a circular path '
               'whose angle measures 0.2 radians with a radius of 80 miles?\n'
               'W) 16\n'
               'X) 40\n'
               'Y) 80\n'
               'Z) 400',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: What is the name for the amount of time it takes for a wave to complete a single '
               'cycle?',
          'a': 'PERIOD'},
         {'q': 'PHYSICS Short Answer: Identify all of the following four forces that are real in inertial reference '
               'frames: 1) Centrifugal; 2) Centripetal; 3) Lorentz; 4) Coriolis.',
          'a': '2, 3'},
         {'q': 'PHYSICS Short Answer: An alpha particle of velocity 600 kilometers per second is fired directly at a '
               'helium-4 nucleus at rest. The two collide completely elastically. What is the final velocity, in '
               'kilometers per second, of the target helium nucleus?',
          'a': '600'},
         {'q': 'PHYSICS Short Answer: Identify all of the following three statements that are always true about '
               'resistors in parallel: 1) The equivalent resistance is greater than any individual resistance; 2)\n'
               'The voltage across each resistor is the same; 3) The current through each resistor is the same.',
          'a': '2'},
         {'q': 'PHYSICS Short Answer: An object is thrown with a horizontal velocity of 20 meters per second from a '
               'height of 125 meters above level ground. If air resistance is negligible, to the nearest whole number, '
               'how many seconds does it take the object to fall to the ground?',
          'a': '5'},
         {'q': 'PHYSICS Short Answer: In volts per meter, what is the electric field at the center of a hollow '
               'metallic sphere with a radius of 10 centimeters when the center of the sphere is 3 meters from a '
               'particle with a charge of 5 coulombs?',
          'a': '0'},
         {'q': 'PHYSICS Short Answer: A model train is towing 3 rail cars full of marbles, with a total kinetic energy '
               'of 100 joules. If the locomotive detaches the rail cars, the total mass of the train is reduced by '
               '50%. If the locomotive then suddenly doubles its speed, what will be its resulting kinetic energy, in '
               'joules?',
          'a': '200'},
         {'q': 'PHYSICS Short Answer: To three significant figures, at what temperature, in kelvins, does pure water '
               'boil at sea level?',
          'a': '373'},
         {'q': 'PHYSICS Short Answer: In a several step production process, the efficiency of Stage 1 is 45 percent, '
               'the efficiency of Stage 2 is 85 percent, and the efficiency of Stage 3 is 15 percent. To the nearest '
               'whole number percent, what is the overall efficiency of process?',
          'a': '6'},
         {'q': 'PHYSICS Short Answer: Measured in newtons, what is the magnitude of the centripetal force on a '
               '10-kilogram object traveling along a circular path with a radius of 50 meters at a velocity of 20 '
               'meters per second?',
          'a': '80'},
         {'q': 'PHYSICS Short Answer: A large block of ice is placed in a water bath maintained at 80 degrees\n'
               'Celsius. After some time, one half of the mass of the ice block has melted. What is the temperature, '
               'in degrees Celsius, of the surface of the remaining ice?',
          'a': '0'},
         {'q': 'PHYSICS Short Answer: A block rests upon an incline of an unknown angle. If the coefficient of static '
               'friction between the block and the incline is one-third times the square root of 3, and the block is '
               'just barely held by friction, what is the angle of the incline to the horizontal, to the nearest '
               'degree?',
          'a': '30'},
         {'q': 'PHYSICS Multiple Choice: An elevator is moving downward with decreasing speed. What are the directions '
               'of its velocity and acceleration?\n'
               'W) Both are upward\n'
               'X) Both are downward\n'
               'Y) Velocity is upward and acceleration is downward\n'
               'Z) Velocity is downward and acceleration is upward',
          'a': 'Z'},
         {'q': 'PHYSICS Short Answer: What is the name given to light produced when a charged particle passes through '
               'a material at a speed faster than the phase velocity of light in that material?',
          'a': 'CHERENKOV RADIATION'},
         {'q': 'PHYSICS Multiple Choice: Ignoring temperature changes, how much of a pressure increase, in pascals, '
               'does a diver feel at 100 meters below the surface of a fresh-water lake?\n'
               'W) 9,800\n'
               'X) 98,000\n'
               'Y) 980,000\n'
               'Z) 9,800,000',
          'a': 'Y'},
         {'q': 'PHYSICS Multiple Choice: What is the name for a particle that carries a half-integer spin?\n'
               'W) Hadron\n'
               'X) Boson\n'
               'Y) Fermion\n'
               'Z) Proton',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: What quantity is defined as the ratio of the charge on an electric component to '
               'the electric potential applied across it?',
          'a': 'CAPACITANCE'},
         {'q': 'PHYSICS Short Answer: Fiber optic cables have revolutionized the information age with the ability to '
               'transfer data at much higher rates than conventional electric cables. Fiber optic cables work because '
               'of total internal reflection, which results from a difference in what optical property between the '
               'cable and surrounding medium?',
          'a': 'REFRACTIVE INDEX'},
         {'q': "PHYSICS Multiple Choice: What is an object's average angular acceleration, in degrees per second per "
               'second, if it transited 72 degrees with an initial angular velocity of 8 degrees per second and a '
               'final angular velocity of 10 degrees per second?\n'
               'W) 1/12\n'
               'X) 1/6\n'
               'Y) 1/4\n'
               'Z) 1/3',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: Very heavy nuclei tend to decay to stability by the emission of a light nucleus '
               'with two neutrons and two protons. What type of decay is this?',
          'a': 'ALPHA'},
         {'q': 'PHYSICS Short Answer: A car is traveling around a flat 200 meter diameter circular track at\n'
               '25 meters per second. What is the centripetal acceleration on this car in meters per second squared?',
          'a': '6.25'},
         {'q': 'PHYSICS Multiple Choice: Which of the following does NOT describe the strong force?\n'
               'W) It is mediated by the W boson\n'
               'X) It is responsible for holding together the nucleus\n'
               'Y) It is carried by gluons\n'
               'Z) It is described with quantum chromodynamics',
          'a': 'W'},
         {'q': 'PHYSICS Multiple Choice: Which of the following bodies has the largest escape speed?\n'
               "W) Earth's moon\n"
               'X) Europa\n'
               'Y) Ganymede [GAN-ih-meed]\n'
               'Z) Pluto',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: What is the name for the change in the direction of propagation of light when it '
               'passes from one transparent material to another?',
          'a': 'REFRACTION'},
         {'q': 'PHYSICS Short Answer: Generally, every time energy is converted from one form to another, there is '
               'less energy available to do useful work. What is the name of the law that states this?',
          'a': 'SECOND LAW OF THERMODYNAMICS'},
         {'q': 'PHYSICS Multiple Choice: Which of the following constants is fundamentally related to the speed of '
               'light?\n'
               'W) Gravitation constant\n'
               'X) Permeability of free space\n'
               'Y) Planck constant\n'
               'Z) Boltzmann constant',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: What is the equivalent resistance, in ohms to the nearest tenth, of a set of 4 '
               'parallel resistors in series with another set of 5 parallel resistors if all of the resistors have a '
               'resistance of 10 ohms?',
          'a': '4.5'},
         {'q': 'PHYSICS Multiple Choice: Which of the following types of electromagnetic energy has the shortest '
               'wavelengths?\n'
               'W) X-rays\n'
               'X) AM radio\n'
               'Y) Infrared\n'
               'Z) Visible',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: If objects A and B have masses of 10 kilograms and 20 kilograms, respectively, '
               'and object A is traveling at 50 meters per second in the positive x direction while object B is '
               'traveling at 30 meters per second in the negative x direction, what is the linear momentum of the '
               'resultant system in kilogram-meters per second after a perfectly inelastic collision?',
          'a': '100 IN THE NEGATIVE X DIRECTION'},
         {'q': 'PHYSICS Multiple Choice: Which of the following leptons has the largest mass?\n'
               'W) Electron neutrino\n'
               'X) Muon\n'
               'Y) Muon neutrino\n'
               'Z) Tauon',
          'a': 'Z'},
         {'q': 'PHYSICS Multiple Choice: What is the SI derived unit for electrical conductance?\n'
               'W) Henry\n'
               'X) Siemens\n'
               'Y) Weber\n'
               'Z) Tesla',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: A pilot is in a recoverable spin with her engine turned off, and with the '
               "plane's nose directed toward the Earth's center. What term describes the limit of her rate of descent?",
          'a': 'TERMINAL VELOCITY'},
         {'q': 'PHYSICS Short Answer: An electron in a hydrogen atom is excited from the n = 1 to n = 2 energy level '
               'by absorbing a photon. Then, it is excited from the n = 2 to the n = 3 energy level by absorbing a '
               'second photon. What is the ratio of the energies of the first photon to the second?',
          'a': '27:5'},
         {'q': 'PHYSICS Multiple Choice: Which of the following is NOT responsible for the failure of a pendulum to '
               'reach the height from which it was released as time progresses?\n'
               'W) Friction\n'
               'X) Gravity\n'
               'Y) Air resistance\n'
               'Z) Damping',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: Undulators are used in light sources to cause emissions of photons from electron '
               'bunches. If the spacing between electromagnets is 5 centimeters, and the electron beam has velocity of '
               '3 x 107 meters per second, what frequency, to the nearest 100 MHz, of light is emitted?',
          'a': '300'},
         {'q': 'PHYSICS Short Answer: The weber is the SI unit for what quantity?', 'a': 'MAGNETIC FLUX'},
         {'q': 'PHYSICS Short Answer: What term describes the balance between gravitational force and the outward gas '
               'pressure in a stable star?',
          'a': 'HYDROSTATIC EQUILIBRIUM'},
         {'q': 'PHYSICS Short Answer: A standard spring mass oscillator on a frictionless surface oscillates at '
               'amplitude 2 meters. At what displacement from equilibrium does the spring store zero potential energy?',
          'a': '0'},
         {'q': 'PHYSICS Short Answer: Identify all of the following four particles that obey Bose-Einstein statistics: '
               '1) Super-cooled helium atoms; 2) Beta particles; 3) Gamma rays; 4) Neutrons.',
          'a': '1 AND 3'},
         {'q': 'PHYSICS Short Answer: A small ball is fired horizontally off the edge of a table at 3 meters per '
               'second, taking 0.4 seconds to hit the ground below. When the ball hits the floor, how far, in meters, '
               'is it horizontally from the edge of the table?',
          'a': '1.2'},
         {'q': 'PHYSICS Short Answer: A rope is oscillated in such a way that it creates a standing wave with a '
               'wavelength of 3 meters and an amplitude of 0.4 meters. What is the distance, in meters, between the '
               'highest and lowest positions of a piece of the rope 0.25 meters from a node?',
          'a': '0.4'},
         {'q': 'PHYSICS Multiple Choice: An infinite number of 1-ohm resistors are connected in parallel so that there '
               'is one on the first branch, two in series on the second branch, three in series on the third, and so '
               'on. What is the overall resistance, in ohms, of this circuit?\n'
               'W) 0\n'
               'X) 2\n'
               'Y) π\n'
               'Z) Natural log of 2',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: What criterion states that two objects are resolvable if the angular separation '
               'between them is enough such that the first diffraction maxima of one object coincides with the minima '
               'of the other?',
          'a': 'RAYLEIGH CRITERION'},
         {'q': 'PHYSICS Short Answer: On a spring break trip, Sarah and her 3 friends run out of gas while driving to '
               'Florida. The nearest gas station is 1.1 kilometers away. If they apply a constant cumulative force of '
               '1200 newtons to the car, how much work will they do, in joules, by pushing the car to the gas station?',
          'a': '1,320,000'},
         {'q': 'PHYSICS Short Answer: An electron is fired through parallel plate electrodes that are 5 millimeters '
               'apart. A 2 millitesla magnetic field is perpendicular to the electric field between the plates, which '
               'have a potential difference of 600 volts. If the electron is NOT deflected, at what speed, in meters '
               'per second and in scientific notation, is it traveling?',
          'a': '6.0 x 107'},
         {'q': 'PHYSICS Short Answer: What general term refers to lighting that uses LEDs as sources of illumination '
               'rather than electrical filaments, plasma, or gas?',
          'a': 'SOLID-STATE LIGHTING'},
         {'q': 'PHYSICS Short Answer: What state of matter, consisting of bosons cooled to nearly absolute zero, '
               'allows for the macroscopic observation of quantum phenomena?',
          'a': 'BOSE-EINSTEIN CONDENSATE'},
         {'q': 'PHYSICS Short Answer: What particular type of Raman scattering occurs when the emitted photon is of '
               'higher wavelength than the incident one?',
          'a': 'STOKES'},
         {'q': 'PHYSICS Short Answer: In the BCS theory of superconductivity, the correlation between two electrons '
               'leads to a reduction in electron scattering that forms the basis of superconductivity. What is the '
               'name of this group of electrons?',
          'a': 'A COOPER PAIR'},
         {'q': 'PHYSICS Multiple Choice: Which of the following statements correctly summarizes the zeroth law of '
               'thermodynamics?\n'
               'W) If each of two systems are in thermal equilibrium with a third system, they must be in thermal '
               'equilibrium with each other\n'
               'X) When energy passes as work, heat, or with matter, into or out of a system, its internal energy '
               'changes in accord with the law of conservation of energy\n'
               'Y) In a natural thermodynamic process, the sum of the entropies of the participating thermodynamic '
               'systems increases\n'
               'Z) The entropy of a system approaches a constant value as the temperature approaches absolute zero',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: Water flowing out of a 2.0 centimeter diameter pipe can fill a 300- liter '
               'bathtub in 5 minutes. In meters cubed per second, what is the flow rate of the pipe?',
          'a': '0.001'},
         {'q': 'PHYSICS Short Answer: An ionization chamber smoke detector uses the radiation from a small amount of '
               'radioactive material to detect the presence of smoke. What type of radiation is it that ionizes oxygen '
               'and nitrogen molecules, providing a steady current in the chamber, and then when impeded by smoke, '
               'disrupts the current, triggering the alarm?',
          'a': 'ALPHA'},
         {'q': 'PHYSICS Short Answer: Matt throws a baseball horizontally from a height of 4 meters. It lands 25 '
               'meters away. What is the horizontal velocity, to the nearest meter per second, of the ball as it '
               "leaves Matt's hand?",
          'a': '28'},
         {'q': 'PHYSICS Short Answer: A 100-kilogram box filled with coffee is sitting on your concrete garage floor. '
               "You decide to move the box, but you're going to push the box rather than lift it. How much force, in "
               'newtons to the nearest integer, must you exert on the box in order to get it moving, if the '
               'coefficient of static friction is 0.25?',
          'a': '245'},
         {'q': 'PHYSICS Multiple Choice: An oscillating system has a characteristic frequency of 10 radians per second '
               'and an effective spring constant of 200 Newtons per meter. What is the effective mass, in kilograms, '
               'of the oscillator?\n'
               'W) 1\n'
               'X) 2\n'
               'Y) 5\n'
               'Z) 10',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: An RC circuit contains a 10-ohm resistor and a 20-millifarad capacitor. How '
               'long, in milliseconds, would it take for the voltage to fall by a factor of e–2?',
          'a': '400'},
         {'q': 'PHYSICS Short Answer: To one significant figure, how fast, in meters per second, would you be moving '
               'if you started at rest and accelerated at a constant rate of one meter per second squared for an '
               'entire year?',
          'a': '30 MILLION'},
         {'q': 'PHYSICS Short Answer: Consider a simple parallel RL circuit connected to an AC power source. The peak '
               'current through the inductor is 10 milliamps. What will the peak current through the inductor become, '
               'in milliamps, if the frequency is halved and the peak voltage is doubled?',
          'a': '40'},
         {'q': 'PHYSICS Multiple Choice: An object is thrown vertically upward at time t = 0, at a speed of 40 meters '
               'per second, from the top of a building that has a height of 100 meters. Assuming acceleration due to '
               'gravity equals 10 meters per second squared, at what time t in seconds will the object hit the '
               'ground?\n'
               'W) 4\n'
               'X) 8\n'
               'Y) 10\n'
               'Z) 15',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: What is the effect by which a material with a small positive magnetic '
               'susceptibility creates a magnetic field in the direction of an applied field?',
          'a': 'PARAMAGNETISM'},
         {'q': 'PHYSICS Short Answer: Also known as braking radiation, what effect occurs when a charged particle is '
               'deflected and undergoes deceleration?',
          'a': 'BREMSSTRAHLUNG'},
         {'q': 'PHYSICS Short Answer: A car is traveling at 30 meters per second. After having traveled 160 meters, it '
               'has accelerated to 50 meters per second. In meters per second squared, what is its average '
               'acceleration during this period?',
          'a': '5'},
         {'q': 'PHYSICS Multiple Choice: Eddy currents are circular electric currents induced by a changing magnetic '
               'field within conductors. Which of the following is NOT an application that utilizes eddy currents?\n'
               'W) Roller coaster braking\n'
               'X) Induction heating\n'
               'Y) Metal detectors\n'
               'Z) Detecting counterfeit bills in vending machines',
          'a': 'Z'},
         {'q': 'PHYSICS Multiple Choice: In a DC/DC converter, the electrical energy is stored in which elements of '
               'the circuit?\n'
               'W) Capacitors and inductors\n'
               'X) Resistive elements\n'
               'Y) Switching element\n'
               'Z) Diodes and protection circuitry',
          'a': 'W'},
         {'q': 'PHYSICS Multiple Choice: What is the equivalent resistance, to the nearest tenth of an ohm, of a '
               'circuit containing 3 resistors in parallel, with resistance values of 5 ohms, 3 ohms, and 6 ohms?\n'
               'W) 1.0\n'
               'X) 1.4\n'
               'Y) 1.8\n'
               'Z) 2.2',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: What fundamental force mediates the decay of a neutron into a proton, an '
               'electron, and a neutrino?',
          'a': 'WEAK FORCE'},
         {'q': 'PHYSICS Multiple Choice: Through which of the following materials does sound travel the fastest?\n'
               'W) Aluminum\n'
               'X) Copper\n'
               'Y) Glass\n'
               'Z) Gold',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: What thermodynamic cycle, most often found in jet engines, uses adiabatic '
               'compression and expansion processes as well as isobaric heating and cooling processes?',
          'a': 'BRAYTON CYCLE'},
         {'q': 'PHYSICS Multiple Choice: A former Russian service officer died in November 2006 after being diagnosed '
               'with acute radiation syndrome. During the investigation into his death, authorities were able to trace '
               'his activities, in part, because his body had excreted trace amounts of which of the following '
               'radioactive isotopes, which he had recently ingested?\n'
               'W) Polonium-210 with a half-life of 138 days\n'
               'X) Bismuth-213 with a half-life of 45 minutes\n'
               'Y) Technetium-99 with a half-life of 6 hours\n'
               'Z) Uranium-238 with half-life of 4.5 billion years',
          'a': 'W'},
         {'q': 'PHYSICS Multiple Choice: What is the name of the postulate of quantum mechanics that requires that '
               'quantum mechanical systems behave classically as quantum numbers approach infinity?\n'
               'W) Correspondence principle\n'
               'X) Born approximation\n'
               'Y) Heisenberg postulate\n'
               'Z) Wigner-Eckart theorem',
          'a': 'W'},
         {'q': 'PHYSICS Multiple Choice: The compressor in a Carnot engine performs which of the following types of '
               'compression?\n'
               'W) Isobaric\n'
               'X) Isotropic\n'
               'Y) Isentropic\n'
               'Z) Isochoric',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: By what process can a quantum particle cross potential energy hills without '
               'expending any energy?',
          'a': 'QUANTUM TUNNELING'},
         {'q': 'PHYSICS Short Answer: What is the potential energy, in joules to one significant figure, stored in the '
               'electric field of a capacitor if its capacitance is 10 to the negative 6 farads with a voltage of 100 '
               'volts?',
          'a': '0.005'},
         {'q': 'PHYSICS Short Answer: Identify all of the following four elements that are most commonly used as '
               'semiconductor material in integrated circuits: 1) Silicon; 2) Copper; 3) Germanium; 4)\n'
               'Indium.',
          'a': '1, 3'},
         {'q': 'PHYSICS Multiple Choice: Which of the following particles does NOT correspond to one of the four basic '
               'types of radiation?\n'
               'W) Electron\n'
               'X) Helium nucleus\n'
               'Y) Photon\n'
               'Z) Lithium nucleus',
          'a': 'Z'},
         {'q': 'PHYSICS Short Answer: What force carrying particle holds quarks together inside of hadrons?',
          'a': 'GLUONS'},
         {'q': "PHYSICS Short Answer: You're standing at home plate on a baseball diamond. From 20 meters away, a "
               'pitcher throws a 100-gram baseball towards you at negative 40 meters per second. The baseball strikes '
               'you in the arm and bounces directly back to the pitcher at +5 meters per second.\n'
               'What impulse, in newton-seconds rounded to the nearest tenth, did your arm deliver to the ball during '
               'the collisions?',
          'a': '+4.5'},
         {'q': 'PHYSICS Short Answer: What dimensionless quantity is usually defined as the useful output of a heat '
               'engine divided by the amount of heat energy input?',
          'a': 'EFFICIENCY'},
         {'q': 'PHYSICS Multiple Choice: By what factor is the intensity of a sound wave multiplied when both angular '
               'frequency and displacement amplitude are halved?\n'
               'W) 1/16\n'
               'X) 1/4\n'
               'Y) 4\n'
               'Z) 16',
          'a': 'W'},
         {'q': 'PHYSICS Short Answer: In the field of electrostatics, integrals of electric field over a closed '
               'surface yield electric flux. What is the term for such a closed surface?',
          'a': 'GAUSSIAN SURFACE'},
         {'q': 'PHYSICS Short Answer: What instrument is designed to measure the presence, direction, and strength of '
               'an electric current in a conductor, with its earliest versions simply consisting of a compass '
               'surrounded by a wire coil?',
          'a': 'GALVANOMETER'},
         {'q': 'PHYSICS Multiple Choice: Which of the following quarks does NOT have negative charge?\n'
               'W) Charm\n'
               'X) Strange\n'
               'Y) Down\n'
               'Z) Bottom',
          'a': 'W'},
         {'q': 'PHYSICS Multiple Choice: Which of the following processes imposes the restriction that the work done '
               'on the system is zero, and the change in internal energy is equal to the heat added?\n'
               'W) Adiabatic\n'
               'X) Constant volume\n'
               'Y) Closed cycle\n'
               'Z) Free expansion',
          'a': 'X'},
         {'q': 'PHYSICS Multiple Choice: A 60-kilogram man holding a 20-kilogram box rides on a skateboard at a speed '
               'of positive 7 meters per second. He throws the box behind him, giving it a velocity of negative 5 '
               'meters per second, with respect to the ground. What is his velocity, in meters per second, after '
               'throwing the object?\n'
               'W) 8\n'
               'X) 9\n'
               'Y) 10\n'
               'Z) 11',
          'a': 'Z'},
         {'q': 'PHYSICS Multiple Choice: Which of the following best describes the electromotive force produced in a '
               'circuit by a changing flux?\n'
               'W) Ampere’s Law\n'
               'X) Faraday’s Law\n'
               'Y) Gauss’ Law\n'
               'Z) Ohm’s Law',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: What is the quantum mechanical property of electrons that causes a beam of '
               'silver atoms to split into two distinct beams as it passes through a magnetic field gradient?',
          'a': 'SPIN'},
         {'q': 'PHYSICS Short Answer: A block starts slipping on a track set at exactly 30 degrees to the horizontal. '
               'What is the coefficient of static friction between the block and track?',
          'a': '√3/3 [SQUARE ROOT OF 3 OVER 3]'},
         {'q': 'PHYSICS Short Answer: In an optical microscope, lenses of plastic and glass direct and focus the '
               'light. What is the name of the distance between the specimen being viewed and the front lens of the '
               'objective?',
          'a': 'OBJECTIVE WORKING DISTANCE'},
         {'q': "PHYSICS Short Answer: What scientist's name is given to the number that is used to characterize "
               'whether a flow is laminar or turbulent?',
          'a': 'OSBORNE REYNOLDS'},
         {'q': 'PHYSICS Multiple Choice: Which of the following characteristics makes Xenon-135 an effective neutron '
               'poison in nuclear reactors?\n'
               'W) Cherenkov radiation from beta decay of Xenon-135\n'
               'X) Full valence shell\n'
               'Y) High thermal neutron capture cross-section\n'
               'Z) Unstable with half-life of 9.2 hours',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: What fraction of the speed of light must a person drive in order that incoming '
               '450 terahertz red light would appear to be 540 terahertz green light?',
          'a': '11/61'},
         {'q': 'PHYSICS Multiple Choice: Taking the acceleration due to gravity to be 10 meters per second squared, '
               'how much power, in watts, is required to lift a 2 kilogram mass at a constant speed of 2 meters per '
               'second?\n'
               'W) 2\n'
               'X) 4\n'
               'Y) 40\n'
               'Z) 80',
          'a': 'Y'},
         {'q': 'PHYSICS Short Answer: Consider the following dispersion relation: omega = 2k2 – 9k + 6.\n'
               'At what two wavenumbers, k, are the group and phase velocity equal?',
          'a': 'SQUARE ROOT OF 3 and NEGATIVE SQUARE ROOT OF 3'},
         {'q': 'PHYSICS Multiple Choice: A disc originally at rest moves through 6 radians as it undergoes a constant '
               'angular acceleration about its central axis. If the time taken to accelerate is 2 seconds, what is the '
               'magnitude of the acceleration in radians per square second?\n'
               'W) 3\n'
               'X) 6\n'
               'Y) 9\n'
               'Z) 12',
          'a': 'W'},
         {'q': 'PHYSICS Multiple Choice: Which of the following types of magnetometers needs to be cooled to very low '
               'temperatures due to reliance on the Josephson effect?\n'
               'W) Overhauser\n'
               'X) SERF [surf]\n'
               'Y) SQUID [squid]\n'
               'Z) Fluxgate',
          'a': 'Y'},
         {'q': 'PHYSICS Multiple Choice: The current in a cathode ray tube is 10 nanoamps. Which of the following is '
               'closest to the number of electrons striking the face of the glass tube each second?\n'
               'W) 3.6 x 1010\n'
               'X) 6.3 x 1010\n'
               'Y) 3.6 x 1011\n'
               'Z) 6.3 x 1011',
          'a': 'X'},
         {'q': 'PHYSICS Short Answer: List two of the experiments performed at the Large Hadron\n'
               'Collider at CERN in Europe.',
          'a': 'Any two of the following: ATLAS, CMS, LHCb, ALICE, ToTEM, LHCf, MoEDAL'},
         {'q': 'PHYSICS Short Answer: How much energy, in joules, is in a single kilo-watt hour?', 'a': '3.6 MILLION'},
         {'q': 'PHYSICS Short Answer: Studies of neutral kaon oscillations resulted in the discovery of what symmetry '
               'violation in particle physics?',
          'a': 'CP VIOLATION'}],
 'energy': [{'q': 'ENERGY Multiple Choice: Which of the following energy sources is most directly derived from the '
                  'sun?\n'
                  'W) Wind\n'
                  'X) Tidal energy\n'
                  'Y) Geothermal\n'
                  'Z) Nuclear',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: Transesterification is a reaction used to generate biodiesel from what class '
                  'of biomolecule?',
             'a': 'TRIGLYCERIDES'},
            {'q': 'ENERGY Short Answer: Uranium pellets that are sealed into fuel rods are composed of what specific '
                  'uranium compound?',
             'a': 'URANIUM DIOXIDE'},
            {'q': 'ENERGY Multiple Choice: What technology provides the vast majority of the worldwide grid energy '
                  'storage capacity?\n'
                  'W) Liquid or compressed air\n'
                  'X) Lead-acid, nickel-cadmium and sodium-sulfur batteries\n'
                  'Y) Hydroelectric pump storage\n'
                  'Z) Superconducting magnetic energy storage',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Which of the following is the most common usage of syngas?\n'
                  'W) Electricity production\n'
                  'X) Transportation\n'
                  'Y) Water heating\n'
                  'Z) Production of ethanol',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: What is the most commonly used process for desulfurizing gas?',
             'a': 'CLAUS PROCESS'},
            {'q': 'ENERGY Short Answer: Identify all the following three categories of fuel cells that can be '
                  'considered types of proton exchange membrane fuel cells? 1) Direct-methanol, 2) Molten carbonate, '
                  '3) Phosphoric acid.',
             'a': '1 AND 3'},
            {'q': 'ENERGY Multiple Choice: Which of the following molecules is used as a standard for determining the '
                  'octane rating of gasoline?\n'
                  'W) 2,2,4-trimethylpentane [try-methil-PEN-tane]\n'
                  'X) N-octane\n'
                  'Y) 3-methylheptane [methil-HEP-tane]\n'
                  'Z) 2,2,3,3-tetramethylbutane [tetrah-methil-BYOO-tane]',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: What is the primary gaseous element of wood gas, a product of gasification?',
             'a': 'NITROGEN'},
            {'q': 'ENERGY Multiple Choice: Which of the following user facilities at the Department of\n'
                  'Energy would be best utilized to determine the building blocks of matter created just after the\n'
                  'Big Bang?\n'
                  'W) Advanced Photon Source\n'
                  'X) Relativistic Heavy Ion Collider\n'
                  'Y) High Flux Isotope Reactor\n'
                  'Z) Synchrotron Radiation Lightsource',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: In what form can excess electrical energy be stored in a flywheel?\n'
                  'W) Rotational kinetic energy\n'
                  'X) Rotational potential energy\n'
                  'Y) Translational momentum\n'
                  'Z) Rotational gravitational energy',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: What is the most commonly used material for the anode in commercial '
                  'lithium-ion batteries?',
             'a': 'GRAPHITE'},
            {'q': 'ENERGY Multiple Choice: Which of the following countries was NOT a major petroleum exporter to the '
                  'United States in 2015?\n'
                  'W) Canada\n'
                  'X) Saudi Arabia\n'
                  'Y) Iran\n'
                  'Z) Venezuela',
             'a': 'Y'},
            {'q': 'ENERGY Short Answer: Sustainable biofuel in Brazil is mostly produced from what plant?',
             'a': 'SUGARCANE'},
            {'q': "ENERGY Short Answer: In large coal and nuclear power plants, the plant's power rating is measured "
                  'in either "megawatts e" or "megawatts t." What does "t" stand for?',
             'a': 'THERMAL'},
            {'q': 'ENERGY Short Answer: Some nuclear fuels contain thorium which undergoes a neutron capture event '
                  'followed by two beta minus decays. What element is produced at the end of these three processes?',
             'a': 'URANIUM'},
            {'q': 'ENERGY Short Answer: What one-carbon alcohol can be used directly as fuel in flex-fuel cars due to '
                  'its high octane rating?',
             'a': 'METHANOL'},
            {'q': 'ENERGY Multiple Choice: Which of the following is the least geographically-restricted form of '
                  'grid-scale energy storage?\n'
                  'W) Pumped hydro\n'
                  'X) Batteries\n'
                  'Y) Compressed air\n'
                  'Z) Hot water',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: Order the following three lightbulb technologies from least to most efficient: '
                  '1) Light-emitting diode; 2) Incandescent; 3) Compact fluorescent.',
             'a': '2, 3, 1'},
            {'q': 'ENERGY Short Answer: Coal gas was largely used for municipal lighting and heating before it was '
                  'supplanted by what fuel source?',
             'a': 'NATURAL GAS'},
            {'q': 'ENERGY Multiple Choice: Which of the following is NOT an advantage of green roofs?\n'
                  'W) Improved waterproofing\n'
                  'X) Improved lifespan of roof\n'
                  'Y) Reduced heating costs\n'
                  'Z) Reduced cooling costs',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Which of the following is NOT a desirable quality in the material used to '
                  'coat nuclear fuel rods?\n'
                  'W) Corrosion resistant\n'
                  'X) High neutron absorption\n'
                  'Y) High hardness\n'
                  'Z) Low reactivity to water',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: The Athabasca oil sands, the largest bitumen deposit in the world, are located '
                  'in what country?',
             'a': 'CANADA'},
            {'q': 'ENERGY Short Answer: Syngas, produced from coal gasification, is made up primarily of what two '
                  'gases?',
             'a': 'CARBON MONOXIDE AND HYDROGEN'},
            {'q': 'ENERGY Short Answer: What type of renewable fuel source consists of long alkyl chain esters '
                  'produced from biolipids?',
             'a': 'BIODIESEL'},
            {'q': 'ENERGY Short Answer: What is the total R-value of a wall with 2 inches of fiberglass batting, with '
                  'R = 3 per inch, and 4 inches of brick, with R = 0.2 per inch?',
             'a': '6.8'},
            {'q': 'ENERGY Short Answer: What operating situation, characterized by a circuit with very little to no '
                  'electrical impedence, can cause lithium ion batteries to generate a lot of heat, sometimes causing '
                  'fires?',
             'a': 'SHORT CIRCUIT'},
            {'q': 'ENERGY Multiple Choice: Which of the following best explains why power transmission lines use high '
                  'voltage?\n'
                  'W) Substation equipment used to transmit power at high voltage is cheaper than equipment for low '
                  'voltage\n'
                  'X) Power loss decreases as the square of the voltage increases\n'
                  'Y) Power loss decreases linearly as the voltage increases\n'
                  'Z) It is safer to transmit power at high rather than low voltage',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: One 42-gallon barrel of crude oil produces approximately how many US '
                  'gallons of gasoline?\n'
                  'W) 10\n'
                  'X) 20\n'
                  'Y) 30\n'
                  'Z) 40',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: During fission in a nuclear reactor, non-fission neutron capture by uranium '
                  'yields heavy elements like americium and plutonium. What are these elements called?\n'
                  'W) Pnictogens [NIK-teh-jins]\n'
                  'X) Chalcogens [CHAWK-eh-jins]\n'
                  'Y) Lanthanides [LAN-tha-nides]\n'
                  'Z) Actinides [AK-tin-ides]',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: What refinery process is used to separate components of petroleum based on '
                  'their boiling points?',
             'a': 'DISTILLATION'},
            {'q': 'ENERGY Short Answer: Landfill gas, a potential source of energy, is mostly composed of what '
                  'specific hydrocarbon?',
             'a': 'METHANE'},
            {'q': 'ENERGY Multiple Choice: Which of the following percentages is closest to the percent of\n'
                  'U.S. electricity generated from fossil fuels in 2014?\n'
                  'W) 30\n'
                  'X) 50\n'
                  'Y) 70\n'
                  'Z) 90',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Which of the following is NOT a type of nuclear reactor currently used in '
                  'the United States?\n'
                  'W) Boiling water\n'
                  'X) Solid sodium\n'
                  'Y) Pressurized water\n'
                  'Z) Liquid metal breeder',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Demand Side Management, as part of smart grids, is a combination of '
                  'programs that allows which of the following?\n'
                  'W) Customers to change their energy consumption patterns based on a varying rate of the cost of '
                  'electricity\n'
                  'X) Generators to change their production patterns based on a varying rate of the cost of '
                  'electricity\n'
                  'Y) Utilities to refund money to customers\n'
                  'Z) Meter readers to be replaced by automated smart electricity meters',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: If a power station is referred to as an underground power station, what '
                  'kind of energy does it generate?\n'
                  'W) Hydroelectric\n'
                  'X) Geothermal\n'
                  'Y) Nuclear\n'
                  'Z) Biomass',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: What is the name of the program that the Environmental Protection\n'
                  'Agency maintains in an effort to identify and promote energy-efficient products and buildings, thus '
                  'reducing pollution and waste?',
             'a': 'ENERGY STAR'},
            {'q': 'ENERGY Multiple Choice: When the sun is directly overhead, if all of the sunlight that reaches a '
                  "single square meter of Earth's surface could be captured and converted to electricity, which of the "
                  'following is closest to the number of 60-watt incandescent light bulbs that could be illuminated?\n'
                  'W) 5\n'
                  'X) 10\n'
                  'Y) 15\n'
                  'Z) 100',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Which of the following procedures is NOT commonly used during drilling to '
                  'recover more oil from the ground?\n'
                  'W) Filling the well with water\n'
                  'X) Pumping nitrogen or carbon dioxide into the well\n'
                  'Y) Injecting polymers into the well\n'
                  'Z) Creating a vacuum in the well',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: What type of battery has relatively high power density and cycle life but low '
                  'energy density, thus making it suitable for starting cars?',
             'a': 'LEAD ACID'},
            {'q': 'ENERGY Multiple Choice: Which of the following numbers is the best estimate for the number of '
                  'kilowatt hours of energy used by an average U.S. home in 2014?\n'
                  'W) 700\n'
                  'X) 11,000\n'
                  'Y) 70,000\n'
                  'Z) 110,000',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: Almost all turbine-based electricity production plants use what liquid as the '
                  'intermediate energy carrier?',
             'a': 'WATER'},
            {'q': 'ENERGY Short Answer: What initiative, created in 2000, encourages green building by promoting '
                  'sustainability in construction and utility-efficient operations and maintenance?',
             'a': 'LEED'},
            {'q': 'ENERGY Short Answer: After about 3 years in a nuclear reactor producing electricity, 1/3 of the '
                  'fuel is removed and replaced. What is the term for fuel taken from the reactor?',
             'a': 'SPENT FUEL'},
            {'q': 'ENERGY Multiple Choice: Which of the following sources of energy is derived from the gravity fields '
                  'of the Sun and the Moon?\n'
                  'W) Solar\n'
                  'X) Ocean thermal\n'
                  'Y) Wind\n'
                  'Z) Ocean tidal',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Which of the following best explains why nickel-cadmium batteries are being '
                  'replaced by other types of batteries?\n'
                  'W) Cadmium is a heavy metal pollutant\n'
                  'X) They are not rechargeable\n'
                  'Y) They do not have a consistent terminal voltage\n'
                  'Z) They rapidly lose the ability to store charge',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: The price of which of the following fuels has the greatest impact on the '
                  'cost of electricity?\n'
                  'W) Nuclear\n'
                  'X) Oil\n'
                  'Y) Coal\n'
                  'Z) Natural Gas',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: What is the name of the strategy that makes use of both electrical and thermal '
                  'output from an electricity generator to greatly increase efficiency?',
             'a': 'COMBINED HEAT AND POWER'},
            {'q': 'ENERGY Multiple Choice: Which of the following is NOT considered a practical source of biodiesel?\n'
                  'W) Animal fat\n'
                  'X) Restaurant oils\n'
                  'Y) Vegetable oils\n'
                  'Z) Essential oils',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Which of the following countries had the largest wind energy capacity in '
                  '2014?\n'
                  'W) India\n'
                  'X) United States\n'
                  'Y) China\n'
                  'Z) Germany',
             'a': 'Y'},
            {'q': 'ENERGY Short Answer: Commercial nuclear power reactors in the U.S. include a material that reduces '
                  'the speed of neutrons to permit fission to occur in the fuel more readily. What is the general term '
                  'for this material?',
             'a': 'MODERATOR'},
            {'q': 'ENERGY Short Answer: Energy can be stored in batteries by converting electrical energy into '
                  'chemical energy. In what device is electrical energy stored as separations of large amounts of '
                  'static charge?',
             'a': 'SUPERCAPACITOR'},
            {'q': 'ENERGY Multiple Choice: Enhanced oil recovery allows residual oil to be produced. Which of the '
                  'following substances allows more oil to be produced when it is injected into a well to lower the '
                  'oil viscosity?\n'
                  'W) A thinner form of oil\n'
                  'X) Solvents\n'
                  'Y) Steam\n'
                  'Z) Saltwater',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Recently, two wind turbines were installed inside the Eiffel Tower.\n'
                  'The energy produced will be enough to power which of the following?\n'
                  'W) The tower’s first floor\n'
                  'X) The entire tower, except for lighting\n'
                  'Y) The lighting for the entire tower\n'
                  'Z) The entire tower including the lighting',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Which of the following is closest to the percentage of energy lost as heat '
                  'in an incandescent light bulb?\n'
                  'W) 30\n'
                  'X) 50\n'
                  'Y) 70\n'
                  'Z) 90',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: In a nuclear power plant, the fission reaction directly yields all but '
                  'which of the following?\n'
                  'W) Neutrons\n'
                  'X) Fission products\n'
                  'Y) Fission gamma rays\n'
                  'Z) Electrical current',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Which U.S. state received over 70% of its electricity from hydroelectric '
                  'power in 2013?\n'
                  'W) Maine\n'
                  'X) Texas\n'
                  'Y) Nebraska\n'
                  'Z) Washington',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: According to the Energy Information Administration, which of the following '
                  'is closest to the net number of barrels of oil per day imported by the United States in\n'
                  '2012?\n'
                  'W) 1 million\n'
                  'X) 10 million\n'
                  'Y) 100 million\n'
                  'Z) 1 billion',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: What type of machine, used by both hydroelectric plants and uranium nuclear '
                  'power plants, converts kinetic energy to electrical energy?',
             'a': 'GENERATOR'},
            {'q': 'ENERGY Short Answer: Characterized by its "rotten-egg smell," what gas released by geothermal '
                  'plants is of great environmental concern?',
             'a': 'HYDROGEN SULFIDE'},
            {'q': "ENERGY Short Answer: If a solar power farm doesn't operate for 28% of the time in a month, what is "
                  'its month-averaged capacity factor?',
             'a': '72%'},
            {'q': 'ENERGY Multiple Choice: Lithium-ion batteries can deliver more than twice the overall voltage '
                  'compared to a similar alkaline battery. What is the term for this energy-per-volume ratio in '
                  'batteries?\n'
                  'W) Power\n'
                  'X) Energy density\n'
                  'Y) Electrical output\n'
                  'Z) Battery density',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Which of the following percentages is closest to the percent of energy used '
                  'in Texas in 2014 that was generated by wind?\n'
                  'W) 10\n'
                  'X) 20\n'
                  'Y) 30\n'
                  'Z) 40',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: Before the electricity from a transmission line reaches an end user like a '
                  'home or business, it passes through a step-down transformer. Identify all of the following changes '
                  'that occur across an ideal step-down transformer: 1) Current decreases; 2) Voltage decreases; 3)\n'
                  'Power decreases.',
             'a': '2'},
            {'q': "ENERGY Multiple Choice: Which of the following is the International Energy Agency's stance on "
                  'energy subsidies?\n'
                  'W) They should be phased out\n'
                  'X) There should be greater international collaboration on subsidies\n'
                  'Y) Subsidies are necessary for energy sustainability\n'
                  'Z) Subsidies are necessary to reduce greenhouse emissions',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Which of the following has the greatest energy content in BTUs?\n'
                  'W) One gallon of gasoline\n'
                  'X) One cord of wood\n'
                  'Y) One kilowatt hour\n'
                  'Z) One therm of natural gas',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: After a nuclear reactor is shut down and fission stops, the fuel continues to '
                  'produce a lower, but significant, amount of heat for several years. What is the term for this '
                  'residual heat energy?',
             'a': 'DECAY HEAT'},
            {'q': 'ENERGY Short Answer: Incomplete combustion of coal results in what toxic, carbon-based gas?',
             'a': 'CARBON MONOXIDE'},
            {'q': 'ENERGY Multiple Choice: Which of the following experimental batteries is able to charge in less '
                  'than a minute?\n'
                  'W) Copper ion\n'
                  'X) Chromium ion\n'
                  'Y) Aluminum ion\n'
                  'Z) Silicon',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: The Montreal Protocol effectively reduced the use of CFCs that damage the '
                  'ozone layer. One group of replacements for CFCs has no effect on the ozone layer but is now '
                  'recognized as greenhouse gases whose use must also be phased out. What group of gases is this?\n'
                  'W) HFCs\n'
                  'X) HFOs\n'
                  'Y) PFCs\n'
                  'Z) HCFCs',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: The Oak Ridge National Laboratory revealed an electric vehicle, patterned '
                  'after a Shelby Cobra, at the 2015 North American International Auto Show that was built using what '
                  'process?',
             'a': '3D PRINTING'},
            {'q': 'ENERGY Multiple Choice: Instead of simply storing CO via carbon capture and storage\n'
                  '2 projects, engineers have developed a use for the captured CO . How is the captured CO being\n'
                  '2 2 used?\n'
                  'W) Generation of electricity\n'
                  'X) Heating of homes\n'
                  'Y) Oil recovery from mature wells\n'
                  'Z) Plant growth in greenhouses',
             'a': 'Y'},
            {'q': 'ENERGY Short Answer: Identify all of the following three statements that illustrate disadvantages '
                  'of hydroelectricity plants: 1) Water used to run the plant may be reliant on precipitation; 2) The '
                  'plants can produce a lot of pollution; 3) Aquatic habitats near the plants may be destroyed.',
             'a': '1 AND 3'},
            {'q': 'ENERGY Multiple Choice: Which of the following establishes renewable energy use goals for the U.S. '
                  'by a specific date?\n'
                  'W) Net Metering Agreement\n'
                  'X) National Renewable Energy Target Contract\n'
                  'Y) Solar Guerrillas Pact\n'
                  'Z) Renewable Energy Portfolio Standards',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: What environmental secondary pollutant results from sulfur dioxide that is '
                  'produced during the combustion of fossil fuels?',
             'a': 'ACID PRECIPITATION'},
            {'q': 'ENERGY Short Answer: During operation of a nuclear power plant, some non-fuel uranium-\n'
                  '238 present in the fuel is converted to a different element, which then acts as fuel to provide '
                  'about\n'
                  '1/3 of the total energy. What is this second element?',
             'a': 'PLUTONIUM'},
            {'q': 'ENERGY Multiple Choice: According to the US Energy Information Administration, which of the '
                  'following is closest to the percentage of worldwide electricity produced using renewable sources in '
                  '2011?\n'
                  'W) 5\n'
                  'X) 20\n'
                  'Y) 30\n'
                  'Z) 50',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Which one of these factors is NOT used for determining what chemicals are '
                  'blended to make gasoline?\n'
                  'W) Season\n'
                  'X) Ease of transportation\n'
                  'Y) Local emission requirements\n'
                  'Z) Cost of components',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: What energy use comprises the greatest percentage of energy used in commercial '
                  'buildings in the US?',
             'a': 'HEATING'},
            {'q': 'ENERGY Short Answer: Uranium-235 and plutonium-239 can be used as fuel in a reactor because they '
                  'are fissile. Uranium-238, the most abundant form of natural uranium, is NOT fissile, but can be '
                  'converted to plutonium by absorbing neutrons. What term describes material that can be converted to '
                  'fuel in this way?',
             'a': 'FERTILE'},
            {'q': 'ENERGY Multiple Choice: Which of the following policies allows users with renewable energy sources '
                  'to sell excess electricity generated to the utility grid and receive compensation?\n'
                  'W) Renewable Energy Portfolio Standards\n'
                  'X) Feed-in Tariff\n'
                  'Y) Net Metering Agreement\n'
                  'Z) Carbon Cap and Trade',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Which of the following countries currently has a full ban on incandescent '
                  'light bulbs?\n'
                  'W) United States\n'
                  'X) Australia\n'
                  'Y) Argentina\n'
                  'Z) Italy',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Which of the following is the best estimate of the percent of electricity '
                  'produced in the United States using petroleum in 2014?\n'
                  'W) 1\n'
                  'X) 5\n'
                  'Y) 10\n'
                  'Z) 15',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: Nearly all residential electricity in the United States is supplied at '
                  'electrical outlets at what voltage, in volts, and frequency in Hertz?',
             'a': '120, 60'},
            {'q': 'ENERGY Multiple Choice: The International Thermonuclear Experimental Reactor, commonly called ITER '
                  '[eat-er] has been designed to produce 500 million watts of output power and is currently scheduled '
                  'to begin plasma experiments in 2020. What type of nuclear fusion method will ITER utilize, once '
                  'completed?\n'
                  'W) Magnetic confinement\n'
                  'X) Inertial confinement\n'
                  'Y) Magnetic pinch\n'
                  'Z) Inertial electrostatic confinement',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: What unrefined chemical by-product of biodiesel production has potential uses '
                  'in the manufacture of industrial chemicals and fuel additives?',
             'a': 'GLYCERIN'},
            {'q': 'ENERGY Multiple Choice: Biogas is comprised primarily of methane and what other gas?\n'
                  'W) Carbon dioxide\n'
                  'X) Carbon monoxide\n'
                  'Y) Nitrogen\n'
                  'Z) Oxygen',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: The theoretical maximum power that can be extracted from a wind turbine is '
                  "dictated by Betz's Law. Which of the following is closest to the maximum percentage of kinetic "
                  'energy that can be captured by a turbine?\n'
                  'W) 33.9\n'
                  'X) 59.3\n'
                  'Y) 74.6\n'
                  'Z) 85.1',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: The Department of Energy’s advanced reactor research supports new designs for '
                  'liquid metal-cooled fast reactors. In these new designs, what metal is used to cool the reactor '
                  'fuel?',
             'a': 'SODIUM'},
            {'q': 'ENERGY Short Answer: What US Environmental Protection Agency regulation mandates that gasoline '
                  'contain a minimal amount of ethanol or other biofuel?',
             'a': 'RENEWABLE FUEL STANDARD PROGRAM'},
            {'q': 'ENERGY Multiple Choice: Which of the following would not be considered a balance-of- system '
                  'component for a stand-alone wind power system?\n'
                  'W) Battery\n'
                  'X) Circuit breaker\n'
                  'Y) Inverter\n'
                  'Z) Turbine',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: What compound, traditionally added as an anti-knocking additive to gasoline, '
                  'was banned in the United States in 1996 due to health and environmental concerns?',
             'a': 'TETRAETHYL LEAD'},
            {'q': 'ENERGY Multiple Choice: Lithium cobalt oxide is most commonly used for what component of a '
                  'lithium-ion battery?\n'
                  'W) Electrolyte\n'
                  'X) Cathode\n'
                  'Y) Enclosure\n'
                  'Z) Anode',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: What country used 100% renewable energy for 75 consecutive days in 2015?\n'
                  'W) Lesotho [leh-SOH-toh]\n'
                  'X) Costa Rica\n'
                  'Y) Norway\n'
                  'Z) Sweden',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: What biological carbon sequestration method uses iron and requires a better '
                  'understanding of iron cycling in marine systems to determine its long-term impacts?\n'
                  'W) Iron geo-reduction\n'
                  'X) Iron sequestration\n'
                  'Y) Iron filtering\n'
                  'Z) Iron fertilization',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: Recent work at Lawrence Berkeley National Laboratory has linked what metal to '
                  "the health of the brain, showing that improper oxidation is not only linked to Alzheimer's disease, "
                  'but also that it modulates spontaneous activity in developing circuits?',
             'a': 'COPPER'}, {'q': 'ENERGY Multiple Choice: Into which of the following products is the largest percentage of a barrel '
                  'of oil refined?\n'
                  'W) Gasoline\n'
                  'X) Heating oil\n'
                  'Y) Jet fuel\n'
                  'Z) Diesel',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: In the U.S., which of the following sectors uses the most biomass energy '
                  'per year?\n'
                  'W) Industrial\n'
                  'X) Transportation\n'
                  'Y) Commercial\n'
                  'Z) Residential',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Most lignite mined in the United States comes from what state?\n'
                  'W) California\n'
                  'X) Wisconsin\n'
                  'Y) Texas\n'
                  'Z) Pennsylvania',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Biodiesel contains less sulfur than petroleum-based diesel. When compared '
                  'to petroleum- based diesel, which of the following is true about biodiesel due to the lower amount '
                  'of sulfur?\n'
                  'W) It produces more pollutants\n'
                  'X) It is a better lubricant\n'
                  'Y) It is a worse lubricant\n'
                  'Z) It has a lower flashpoint',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: Researchers at Lawrence Berkeley National Lab are currently using statistical '
                  'methods to determine the destiny of every cell in the Drosophila [droh-SAWF-il-ah] zygote '
                  '[ZYE-goat] as it becomes an adult, as has been previously done for C. elegans. What is the term for '
                  'this methodology?',
             'a': 'FATE MAPPING'},
            {'q': 'ENERGY Short Answer: While most US bioethanol is produced from corn, most US biodiesel is produced '
                  'from what crop?',
             'a': 'SOY'},
            {'q': 'ENERGY Multiple Choice: Which of the following does not perform a chemical reaction during '
                  'operation?\n'
                  'W) Combustion engine\n'
                  'X) Rocket engine\n'
                  'Y) Batteries\n'
                  'Z) Wind turbine',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Which of the following best explains why propane is stored in liquid form '
                  'rather than as a gas?\n'
                  'W) It is less flammable as a liquid\n'
                  'X) It takes up much less space as a liquid\n'
                  'Y) It is easier to burn as a liquid\n'
                  'Z) It is a liquid at room temperature',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: What nonrenewable energy source represents the greatest percentage of US '
                  'energy consumption?\n'
                  'W) Coal\n'
                  'X) Natural gas\n'
                  'Y) Propane\n'
                  'Z) Petroleum',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: According to the U.S. Energy Information Administration, which of the '
                  'following sectors consumed the most energy in the United States in 2014?\n'
                  'W) Commercial\n'
                  'X) Residential\n'
                  'Y) Transportation\n'
                  'Z) Industrial',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: DOE researchers are studying unique chemical bonds formed by interactions '
                  'between lithium cations [CAT-eye-onz] and organo-aluminum compounds. Which of the following bonds '
                  'are formed by these interactions?\n'
                  'W) Two-center one-electron bonds\n'
                  'X) Two-center two-electron bonds\n'
                  'Y) Three-center two-electron bonds\n'
                  'Z) Four-center one-electron bonds',
             'a': 'Y'},
            {'q': 'ENERGY Short Answer: Identify all of the following three statements that are true regarding ethanol '
                  'fuel: 1) E15 is a renewable fuel; 2) Ethanol blender pumps are most commonly found in the Midwest; '
                  '3) E15 produces less carbon monoxide emissions than pure gasoline.',
             'a': '2 AND 3'},
            {'q': 'ENERGY Multiple Choice: Which of the following energy sources produces the least carbon dioxide per '
                  'unit of energy?\n'
                  'W) Oil\n'
                  'X) Coal\n'
                  'Y) Natural gas\n'
                  'Z) Nuclear',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Fuel cell vehicles are commercially available in the U.S. How is the '
                  'hydrogen fuel stored on these vehicles?\n'
                  'W) As a gas at 8000 psi\n'
                  'X) As a liquid under cryogenic conditions\n'
                  'Y) Absorbed in metal hydrides\n'
                  'Z) Adsorbed in ceramic zeolites',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: DOE scientists have recently been studying the material properties of '
                  'graphene. Which of the following pairs of characteristics did they discover regarding graphene?\n'
                  'W) High strength, high toughness\n'
                  'X) High strength, low toughness\n'
                  'Y) Low strength, high toughness\n'
                  'Z) Low strength, low toughness',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Which of the following is derived from kerosene?\n'
                  'W) Gasoline\n'
                  'X) Paraffin wax\n'
                  'Y) Jet fuel\n'
                  'Z) Propane',
             'a': 'Y'},
            {'q': 'ENERGY Short Answer: Muliple Choice 97% of US gasoline sold today contains what percentage of '
                  'ethanol?\n'
                  'W) 0\n'
                  'X) 10\n'
                  'Y) 15\n'
                  'Z) 85',
             'a': 'X) 10'},
            {'q': 'ENERGY Short Answer: In the United States, what is the maximum percentage of ethanol upon which a '
                  '"flex-fuel" vehicle is designed to run?',
             'a': '85'},
            {'q': 'ENERGY Multiple Choice: Wind, moving water, sunlight, and heat from Earth’s interior are sources of '
                  'what type of energy?\n'
                  'W) Renewable\n'
                  'X) Fossil\n'
                  'Y) Alternative\n'
                  'Z) Reusable',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Which of the following was not one of the top three carbon-dioxide-emitting '
                  'countries in\n'
                  '2014?\n'
                  'W) India\n'
                  'X) China\n'
                  'Y) United States\n'
                  'Z) Russia',
             'a': 'Z'},
            {'q': "ENERGY Multiple Choice: At the DOE's Advanced Photon Source, researchers are studying industrial "
                  'catalysts used in petrochemical processing. Which of the following correctly describes most of '
                  'these catalysts?\n'
                  'W) Organic molecules\n'
                  'X) Enzymes\n'
                  'Y) Homogeneous inorganic\n'
                  'Z) Heterogeneous inorganic',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Lawrence Berkeley National Lab scientists have been studying XPG, a protein '
                  'found to play a role in protecting the body from cancer. Which of the following proteins likely '
                  'plays a similar role to XPG?\n'
                  'W) Phosphofructokinase [faws-fo-frook-toh-KYE-nase]\n'
                  'X) p53\n'
                  'Y) Aldolase\n'
                  'Z) Carbonic anhydrase',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: While fluorescent lamps have a much higher efficiency than incandescent bulbs, '
                  'they require special disposal concerns due to their construction involving what heavy metal vapor?',
             'a': 'MERCURY'},
            {'q': 'ENERGY Short Answer: What are the coolant and the moderator, respectively, in pressurized heavy '
                  'water reactors?',
             'a': 'HEAVY WATER AND HEAVY WATER'},
            {'q': 'ENERGY Multiple Choice: Which of the following forms of energy has the lowest average cost of '
                  'operation and maintenance?\n'
                  'W) Solar\n'
                  'X) Wind\n'
                  'Y) Geothermal\n'
                  'Z) Hydro',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: One of the largest solar power plants in the U.S. is at Ivanpah '
                  '[EYE-van-pah] in southern\n'
                  'California. It converts solar energy into electricity via what mechanism?\n'
                  'W) Molten salt contacting thermoelectrics\n'
                  'X) Direct photovoltaic [photo-vawl-TAY-ik] panels\n'
                  'Y) Photoelectrolysis to produce hydrogen gas\n'
                  'Z) Superheated steam through a turbine',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Immediately after being removed from a fission reactor, spent fuel rods '
                  'will be placed where?\n'
                  'W) Underground\n'
                  'X) Underwater\n'
                  'Y) Reprocessing plants\n'
                  'Z) MOX factories',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: What are the primary mobile charge carriers in the sulfonated fluoropolymer '
                  '[floor-oh-PAWL-ih-mur] ion-exchange membranes used in commercial fuel cells?\n'
                  'W) Hydroxide ions\n'
                  'X) Sodium cations [CAT-eye-onz]\n'
                  'Y) Water\n'
                  'Z) Protons',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: Moderators in nuclear reactors are used because of their ability to absorb '
                  'energy from what particles?',
             'a': 'NEUTRONS'},
            {'q': 'ENERGY Short Answer: DOE researchers recently published about the development of a complex oxide '
                  'alloy that, rather than being primarily stabilized by chemical bonding, is stabilized by what state '
                  'function?',
             'a': 'ENTROPY'},
            {'q': 'ENERGY Short Answer: Methyl-tertiary-butyl-ether [methil-ter-shee-air-ee- byu-til-eethur], '
                  'abbreviated MTBE, replaced lead in gasoline due to several environmental benefits. In order to '
                  'raise octane rating in current gasoline, what has subsequently replaced MTBE?',
             'a': 'ETHANOL'},
            {'q': 'ENERGY Multiple Choice: Which of the following is the best estimate of the electricity consumption '
                  'of a petascale\n'
                  '[PEH-tah-scale] supercomputer today?\n'
                  'W) 8 kilowatts\n'
                  'X) 80 kilowatts\n'
                  'Y) 8 megawatts\n'
                  'Z) 80 megawatts',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Which of the following weather conditions and times of year is best for '
                  'achieving efficient energy conversion in a solar thermal plant?\n'
                  'W) Partly cloudy day in fall\n'
                  'X) Rainy day in spring\n'
                  'Y) Partly sunny day in winter\n'
                  'Z) Overcast day in summer',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Which of the following accounts for the largest proportion of total US '
                  'domestic energy production?\n'
                  'W) Natural gas\n'
                  'X) Petroleum\n'
                  'Y) Coal\n'
                  'Z) Nuclear',
             'a': 'W'},
            {'q': 'ENERGY Short Answer: DOE scientists recently published a paper in which nanoscale circuitry '
                  '[sur-cah-tree] was developed by printing a carbon-based semiconductor on a germanium '
                  '[jer-MAYN-ee-um] surface. What allotrope of carbon are the semiconductors based on?',
             'a': 'GRAPHENE'},
            {'q': 'ENERGY Short Answer: What is the only baseload electrical power source in the US that is virtually '
                  'carbon neutral, and supplies 20% of baseload electrical power?',
             'a': 'NUCLEAR POWER'},
            {'q': 'ENERGY Short Answer: Biogas is a renewable energy source that is typically produced as landfill '
                  'gas, caused by the breakdown of biodegradable waste via anaerobic microbes. What two gases are the '
                  'primary constituents of biogas?',
             'a': 'METHANE AND CARBON DIOXIDE'},
            {'q': 'ENERGY Short Answer: Based on average operating conditions, rank the following household appliances '
                  'in order of increasing electricity usage per unit time: 1) LCD TV; 2) Toaster oven; 3) Hair dryer; '
                  '4) Curling iron.',
             'a': '1, 4, 2, 3'},
            {'q': 'ENERGY Short Answer: The National Renewable Energy Laboratory has recently demonstrated that wind '
                  'turbines can now increase the stability of a power system by employing what modulating technology?',
             'a': 'ACTIVE POWER CONTROLS'},
            {'q': 'ENERGY Short Answer: A major component of gasification-based syngas is carbon monoxide. What is the '
                  'other major fuel component?',
             'a': 'HYDROGEN'},
            {'q': 'ENERGY Short Answer: What treaty, signed by the United States, banned the usage of CFCs?',
             'a': 'MONTREAL TREATY'},
            {'q': 'ENERGY Short Answer: Until the 1900s, what fossil fuel was the number one energy source in the '
                  'United States?',
             'a': 'COAL'},
            {'q': 'ENERGY Short Answer: What US state is responsible for generating the most total net electricity?',
             'a': 'TEXAS'},
            {'q': 'ENERGY Short Answer: Vapor extraction, steam-assisted gravity drainage, and cold heavy oil '
                  'production with sand are all methods of extracting what type of petroleum deposit, found primarily '
                  'in Alberta, Canada?',
             'a': 'OIL SANDS'},
            {'q': 'ENERGY Short Answer: What is the name of the process by which biomass is thermally decomposed in '
                  'the absence of oxygen?',
             'a': 'PYROLYSIS'},
            {'q': 'ENERGY Short Answer: What name is used for the semiconductor nanoparticles that are being studied '
                  'and incorporated into solar cells, LEDs, and color displays?',
             'a': 'QUANTUM DOTS'},
            {'q': 'ENERGY Short Answer: DOE scientists at SLAC have previously shown that electrons can be accelerated '
                  'by riding a wave of plasma. Recently, they showed that what similar particles, products of beta '
                  '[BAY-tah] plus decay, can also be accelerated in the same manner?',
             'a': 'POSITRONS'},
            {'q': 'ENERGY Short Answer: Identify all of the following three emissions that are reduced in biodiesel as '
                  'compared to petroleum diesel: 1) Sulfur; 2) Particulates; 3) Carbon monoxide.',
             'a': 'ALL OF THEM'},
            {'q': 'ENERGY Short Answer: E10 fuel can produce what low atmosphere pollutant that serves as a UV '
                  'protectant in the upper atmosphere?',
             'a': 'OZONE'},
            {'q': 'ENERGY Short Answer: The Daya [DIE-ah] Bay Collaboration is currently on the hunt for a '
                  'hypothetical type of neutrino [new-TREE-no] that does not interact with other particles except '
                  'through gravity. What is the term for this neutrino?',
             'a': 'STERILE NEUTRINO'},
            {'q': 'ENERGY Short Answer: Renewable diesel is produced via multiple methods. Biodiesel, however, is only '
                  'produced via what chemical process?',
             'a': 'TRANSESTERIFICATION'},
            {'q': 'ENERGY Short Answer: Scientists at Argonne National Lab recently published a paper regarding the '
                  'potential use of certain microbes as a method for recovering natural gas from depleted oil and coal '
                  'mines. What specific fuel molecule do these microbes produce?',
             'a': 'METHANE'},
            {'q': 'ENERGY Short Answer: DOE scientists at Brookhaven National Lab are using the Relativistic Heavy Ion '
                  'Collider to study color confinement within protons. What group of elementary particles are they '
                  'studying?',
             'a': 'QUARKS'},
            {'q': 'ENERGY Short Answer: Many redox [REE-dox] flow batteries use acidic electrolytes. Electrodes in '
                  'these devices must necessarily be immune to acid attack as well as electronically conductive. What '
                  'element is used for almost all flow battery electrodes?',
             'a': 'CARBON'},
            {'q': 'ENERGY Short Answer: What U.S. university was the site of the first ever sustained nuclear '
                  'reaction?',
             'a': 'UNIVERSITY OF CHICAGO'},
            {'q': 'ENERGY Short Answer: Recent experiments regarding antimatter at the Relativistic Heavy Ion Collider '
                  'determined that what fundamental force demonstrates no asymmetry within nuclei [NEW-klee-eye]?',
             'a': 'STRONG NUCLEAR FORCE'},
            {'q': 'ENERGY Short Answer: Identify all of the following three options that would increase the resistance '
                  'of a wire:\n'
                  '1) Increasing the temperature; 2) Increasing the radius; 3) Increasing the length.',
             'a': '1 AND 3'},
            {'q': 'ENERGY Short Answer: Hydrogen fuel cells use a membrane to separate the electrodes and allow what '
                  'particles to pass from the anode [ANN-ode] to the cathode [CATH-ode]?',
             'a': 'PROTONS'},
            {'q': 'ENERGY Multiple Choice: What is the typical co-electrolyte in Vanadium [vah-NAY-dee-um] redox '
                  '[REE-dox] flow batteries?\n'
                  'W) Zinc nitrate\n'
                  'X) Sulfuric acid\n'
                  'Y) Sodium hydroxide\n'
                  'Z) Copper chloride',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: Biodiesel produces less particulates, carbon oxides, sulfur dioxide, and '
                  'unburnt carbons than fossil-based diesel. However, biodiesel does result in greater emissions of '
                  'what ozone-generating pollutant?',
             'a': 'NITROUS OXIDES'},
            {'q': 'ENERGY Multiple Choice: Which of the following solar cell systems has the highest efficiency?\n'
                  'W) Silicon\n'
                  'X) Gallium [GAL-ee-um] Arsenide [AHR-sin-ide]\n'
                  'Y) Thin Film Photovoltaic [photo-vawl-TAY-ik]\n'
                  'Z) Polymeric [paw-lih-MARE-ik] Photovoltaic',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Which of the following materials would most likely be used as a catalyst '
                  'for fuel cells?\n'
                  'W) Titanium\n'
                  'X) Silver\n'
                  'Y) Carbon\n'
                  'Z) Palladium [puh-LAID-ee-um]',
             'a': 'Z'},
            {'q': 'ENERGY Short Answer: Rank the following three substances in order of increasing energy density: 1) '
                  'Bituminous coal; 2) Gasoline; 3) TNT.',
             'a': '3, 1, 2'},
            {'q': 'ENERGY Multiple Choice: Metal-organic frameworks, or MOFs, are a subject of research at Lawrence '
                  'Berkeley\n'
                  'National Lab. Which of the following is a potential use of MOFs?\n'
                  'W) Tools for quantum computing\n'
                  'X) Developing more accurate predictions via density functional theory\n'
                  'Y) Efficient storage of gases\n'
                  'Z) Homogeneous catalysts',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: DOE scientists at SLAC [slack] have been using the Linac Coherent Light '
                  'Source to study SNARE proteins in the brain. Which of the following processes are SNARE proteins '
                  'involved with?\n'
                  'W) Vesicle docking\n'
                  'X) Actin polymerization [pawl-ih-mer-eh-ZAY-shun]\n'
                  'Y) Intracellular trafficking\n'
                  'Z) Hormonal signalling',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Researchers at Lawrence Berkeley National Lab are currently working on '
                  'optimizing plants to produce less lignin. For which of the following are these genetically modified '
                  'plants likely to be used?\n'
                  'W) Construction materials\n'
                  'X) Ethanol production\n'
                  'Y) Insulation\n'
                  'Z) Food',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Which of the following percentages is closest to the level of engine '
                  'efficiency in a modern gasoline-burning automobile?\n'
                  'W) 10%\n'
                  'X) 25%\n'
                  'Y) 50%\n'
                  'Z) 90%',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: A family in Phoenix is considering installing a photovoltaic '
                  '[photo-vawl-TAY-ik] system on their house. Which of the following roof orientations and inclined '
                  'angles relative to horizontal is best to install the panels?\n'
                  'W) West-facing at 30 degrees\n'
                  'X) South-facing at 30 degrees\n'
                  'Y) South-facing at zero degrees\n'
                  'Z) East-facing at zero degrees',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Why is solar power underutilized in American households?\n'
                  'W) It increases the price of a home by about 5-10%\n'
                  'X) North America is mostly cloudy\n'
                  'Y) Solar technology is currently not very effective\n'
                  'Z) Solar cells are not effective in cold climates',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Nanolithography is a current research interest at Lawrence Livermore '
                  'National Lab.\n'
                  'Which of the following correctly describes nanolithography?\n'
                  'W) The study of fluids confined to nanoscale structures\n'
                  'X) Usage of nanoparticles as medical technology\n'
                  'Y) Depositing residues thinner than 100 nanometers onto surfaces\n'
                  'Z) Fabricating structures smaller than 100 nanometers',
             'a': 'Z'},
            {'q': 'ENERGY Multiple Choice: Researchers are using the Argonne Leadership Computing Facility to design '
                  'and model peptide therapeutics. Which of the following is NOT a challenge associated with peptide '
                  'therapeutics?\n'
                  'W) They are difficult to deliver\n'
                  'X) They have poor specificity\n'
                  'Y) They have poor cell penetration\n'
                  'Z) They are degraded in the circulatory system',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Researchers at Lawrence Livermore National Lab are studying the conditions '
                  'under which planet formation occurs by doing which of the following?\n'
                  'W) Determining the melting point of silica at gigapascal [gih-gah-pass-KAL] pressures\n'
                  'X) Determining the melting point of silica in ultra high vacuum\n'
                  'Y) Determining the boiling point of silica at gigapascal pressures\n'
                  'Z) Determining the boiling point of alumina at gigapascal pressures',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: The Advanced Light Source can be used to identify elements in batteries and '
                  'fuel cells.\n'
                  'Which of the following tools is most likely used for these purposes at the ALS?\n'
                  'W) Fluorescence microscopy\n'
                  'X) X-ray absorption spectroscopy [spek-TRAW-scuh-pee]\n'
                  'Y) NMR spectroscopy [spek-TRAW-scuh-pee]\n'
                  'Z) Confocal microscopy',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Researchers at the Joint Genome [JEE-nome] Institute have been using new '
                  'types of fungi [fun-ji] to produce biofuels from plant material. Where are these fungi naturally '
                  'found?\n'
                  'W) Forest soils\n'
                  'X) Coral reefs\n'
                  'Y) Animal guts\n'
                  'Z) Swamps',
             'a': 'Y'},
            {'q': 'ENERGY Short Answer: In fluidized bed combustors used for clean coal, what is added to the coal to '
                  'keep pollutants in check?',
             'a': 'LIMESTONE'},
            {'q': 'ENERGY Short Answer: The great majority of the transistors in integrated circuits are of the CMOS '
                  'type. What do the letters of the acronym represent?',
             'a': 'COMPLEMENTARY METAL OXIDE SEMICONDUCTOR'},
            {'q': 'ENERGY Multiple Choice: Brookhaven National Lab scientists recently made strides on understanding '
                  'the nature of\n'
                  'Cooper pairs. To which of the following disciplines is this discovery most relevant?\n'
                  'W) Particle physics\n'
                  'X) Superconductor physics\n'
                  'Y) Nuclear physics\n'
                  'Z) Computational chemistry',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: Scientists at Argonne National Lab are using x-rays to probe porosity in '
                  '3D-printed titanium alloys. Which of the following best explains why porosity is undesirable?\n'
                  'W) Porosity decreases resistance to fatigue\n'
                  'X) Porosity decreases flexibility\n'
                  'Y) A large range of pore sizes reduces printing resolution\n'
                  'Z) Porosity limits the size of the structures that can be printed',
             'a': 'W'},
            {'q': 'ENERGY Multiple Choice: Which of the following sources of electricity had the largest increase in '
                  'capacity in the US between 1990 and 2013?\n'
                  'W) Nuclear\n'
                  'X) Coal\n'
                  'Y) Natural gas\n'
                  'Z) Petroleum',
             'a': 'Y'},
            {'q': 'ENERGY Multiple Choice: Most lignite is used for what purpose in the US?\n'
                  'W) Municipal heating\n'
                  'X) Electricity\n'
                  'Y) Automobile fuel\n'
                  'Z) Liquefaction',
             'a': 'X'},
            {'q': 'ENERGY Short Answer: In 1918, the German mathematician Emmy Noether [Noh-tur] published a theorem '
                  'that shows that every conservation law has a corresponding symmetry of the system. What dynamical '
                  'quantity is conserved in a system with rotational symmetry?',
             'a': 'ANGULAR MOMENTUM'},
            {'q': 'ENERGY Short Answer: Solid oxide fuel cells can operate at temperatures as high as 1000 degrees '
                  'Celsius. This high temperature enables these fuel cells to forgo what costly component of '
                  'low-temperature fuel cells?',
             'a': 'CATALYST'},
            {'q': 'ENERGY Short Answer: Scientists at Argonne National Lab are using computational chemistry to probe '
                  'the catalytic properties of iridium [ih-RID-ee-um] oxide nanoparticles. What computational method, '
                  'descended from Hartree-Fock theory, is most commonly used for quantum mechanical modeling?',
             'a': 'DENSITY FUNCTIONAL THEORY'},
            {'q': 'ENERGY Short Answer: Scientists at Brookhaven National Lab discovered that layering graphene on top '
                  "of soda- lime glass resulted in a large change in the graphene's electronic properties. What "
                  'specific element in the glass was found to be responsible for these changes?',
             'a': 'SODIUM'},
            {'q': 'ENERGY Multiple Choice: The energy price spikes in the 1970s and in 2008 suggested which of the '
                  'following about\n'
                  'U.S. energy usage?\n'
                  'W) Usage rises in response to rising prices\n'
                  'X) Usage stays the same when prices rise\n'
                  'Y) Usage drops in response to rising prices\n'
                  'Z) There was no consistent trend about U.S. energy usage',
             'a': 'Y'},
            {'q': 'ENERGY Short Answer: What country is the source of the largest percentage of petroleum imported to '
                  'the US?',
             'a': 'CANADA'},
            {'q': 'ENERGY Short Answer: In a junction transistor used as a switch, which terminal controls the current '
                  'through the other two terminals?',
             'a': 'BASE'},
            {'q': 'ENERGY Multiple Choice: Oil shale is a type of organic-rich sedimentary rock that can be used to '
                  'produce shale oil, also known as tight oil, which is a substitute for conventional crude oil. Which '
                  'of the following varieties of oil shale is\n'
                  'NOT classified as a marine shale?\n'
                  'W) Kukersite\n'
                  'X) Torbanite\n'
                  'Y) Tasminite\n'
                  'Z) Marinite',
             'a': 'X'},
            {'q': 'ENERGY Multiple Choice: The further advancement of rechargeable batteries is currently hindered by '
                  'unavoidable growth of what during battery cell recharge?\n'
                  'W) Lithium dendrites\n'
                  'X) Potassium salts\n'
                  'Y) Nickel deposits\n'
                  'Z) Lead precipitates',
             'a': 'W'},
            {'q': "ENERGY Multiple Choice: Lawrence Livermore National Laboratory's National Ignition Facility is "
                  'using what technology to further nuclear fusion energy research?\n'
                  'W) Magnetic plasma confinement\n'
                  'X) Toroidal plasma confinement\n'
                  'Y) Laser inertial confinement\n'
                  'Z) Electromagnetic implosion',
             'a': 'Y'}],
 'chem': [{'q': 'CHEMISTRY Multiple Choice: Which of the following molecules is nonpolar?\n'
                'W) Acetone\n'
                'X) Carbon tetrachloride\n'
                'Y) Sulfur dioxide\n'
                'Z) Iodine chloride',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following describes the phenomenon of light emission by '
                'fireflies?\n'
                'W) Absorption\n'
                'X) Chemiluminescence [kem-ee-loo-min-ESS-ense]\n'
                'Y) Fluorescence\n'
                'Z) Incandescence',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three types of chemical bonds that can be '
                'formed by two atomic p-orbitals: 1) Sigma bond; 2) Pi [pie] bond; 3) Delta bond.',
           'a': '1 AND 2'},
          {'q': 'CHEMISTRY Short Answer: Identify the central atom hybridization states of the following three '
                'molecules:\n'
                '1) Phosphorous trichloride; 2) Iodine pentafluoride; 3) Formaldehyde.',
           'a': '1) sp3; 2) d2sp3'},
          {'q': 'CHEMISTRY Multiple Choice: According to Lewis theory, which of the following conditions would most '
                'accelerate an acid-base reaction?\n'
                'W) An elevated HOMO [HO-mo] and a depressed LUMO [LOO-mo]\n'
                'X) An elevated HOMO and an elevated LUMO\n'
                'Y) A depressed HOMO and an elevated LUMO\n'
                'Z) A depressed HOMO and a depressed LUMO',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: Consider the reaction of 1 mole of nitrogen gas and 1 mole of oxygen gas to '
                'generate 2 moles of NO gas. In air at 20 degrees Celsius, the equilibrium abundance of NO is about '
                'one part in 1016. To one significant figure and in scientific notation, what is the equilibrium '
                'constant of this reaction?',
           'a': '6 TIMES 10-32'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following graphs would produce a straight line if plotted for '
                'a zero- order irreversible reaction?\n'
                'W) Concentration versus time\n'
                'X) Inverse concentration versus time\n'
                'Y) Log of concentration versus time\n'
                'Z) Inverse concentration squared versus time',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three acids from least to greatest in terms of acidity:\n'
                '1) 2-chlorobutanoic [two kloro-byu-tan-OH-ik] acid; 2) 3-chlorobutanoic acid; 3) 4-chlorobutanoic '
                'acid.',
           'a': '3, 2, 1'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following elements is the most electronegative?\n'
                'W) Beryllium\n'
                'X) Sodium\n'
                'Y) Calcium\n'
                'Z) Cesium',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is an assumption of the ideal gas law?\n'
                'W) The volume of individual molecules is negligible compared to the volume of the container\n'
                'X) All molecules travel at the same velocity\n'
                'Y) Molecules only interact through dipole [DYE-pole]-dipole forces\n'
                'Z) Molecules do not collide with each other',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: How many d electrons are present in a cobalt ion in the +2 state?', 'a': '7'},
          {'q': 'CHEMISTRY Short Answer: Rank the following four elements in terms of increasing melting point:\n'
                '1) Boron; 2) Sodium; 3) Lithium; 4) Tungsten.',
           'a': '2, 3, 1, 4'},
          {'q': 'CHEMISTRY Multiple Choice: What is the most likely type of interaction between the side chains of the '
                'amino acids leucine [LOO-seen] and phenylalanine [Fennel-AL-ah-neen]?\n'
                'W) Ionic\n'
                'X) Hydrophobic\n'
                'Y) Hydrogen bonding\n'
                'Z) Dipole [DYE-pole]-dipole',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Consider the SN2 reaction of 1-chloropentane with the azide [AY-zide] ion. '
                'What is the\n'
                'LUMO [LOO-mo] of the electrophile in this reaction?',
           'a': 'SIGMA-STAR ORBITAL'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements concerning enthalpy '
                '[EN-thul-pee] that are TRUE: 1) The enthalpy [EN-thul-pee] of formation of diamond is equal to zero; '
                '2) The enthalpy change of an isothermal contraction is less than zero; 3) The enthalpy of solution of '
                'ammonium nitrate is greater than zero.',
           'a': '3'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds that have a standard enthalpy '
                'of formation of zero: 1) Ozone; 2) Diamond; 3) Rhombic sulfur.',
           'a': '3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following atoms is commonly found in a +3 oxidation state?\n'
                'W) Calcium\n'
                'X) Nickel\n'
                'Y) Iron\n'
                'Z) Zirconium',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following properties that are examples of state '
                'functions:\n'
                '1) Volume; 2) Temperature; 3) Entropy [EN-troh-pee].',
           'a': '1, 2, 3'},
          {'q': 'CHEMISTRY Short Answer: What is the shape of an isolated complex in which a metal ion is bonded to '
                'six ligands\n'
                '[LIH-gunz]?',
           'a': 'OCTAHEDRAL'},
          {'q': 'CHEMISTRY Short Answer: Rank the boiling points of the following three hydrocarbons, from lowest to '
                'highest:\n'
                '1) Isobutane; 2) Butane; 3) Pentane.',
           'a': '1, 2, 3'},
          {'q': 'CHEMISTRY Multiple Choice: Consider an ideal gas initially occupying a volume of 5 liters and at a '
                'pressure of 5 atmospheres, that undergoes an adiabatic [ad-ee-ah-BAT-ik] expansion to a final '
                'pressure of 1 atmosphere. Which of the following is TRUE concerning the final volume of the gas?\n'
                'W) It is greater than 25 liters\n'
                'X) It is equal to 25 liters\n'
                'Y) It is between 5 liters and 25 liters\n'
                'Z) It is equal to 5 liters',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: What class of microporous aluminosilicates [ah-lumin-oh-SILL-ih-kets] is used '
                'to soften hard water by removing metal ions such as iron and replacing them with sodium?',
           'a': 'ZEOLITES'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three solutions that would be acidic: 1) A '
                'solution of iron(III) atoms hexacoordinated by water molecules; 2) A solution of ammonium sulfate; 3) '
                'A solution of sodium cyanide.',
           'a': '1 AND 2'},
          {'q': 'CHEMISTRY Short Answer: The compound sulfurous [sul-FYUR-us] acid has a first pKa of approximately '
                '1.8 and a second pKa of approximately 7.2. To one decimal place, what is the pH of a solution of 0.1 '
                'molar sodium bisulfite?',
           'a': '4.5'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is considered a strong acid?\n'
                'W) Hydrofluoric acid\n'
                'X) Nitric acid\n'
                'Y) Formic acid\n'
                'Z) Nitrous acid',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following polyprotic [polly-PRO-tic] acids has only two pKa '
                'values?\n'
                'W) Ascorbic acid\n'
                'X) Phosphoric [faws-FOR-ik] acid\n'
                'Y) Arsenic acid\n'
                'Z) Citric acid',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: What gas, whose methylated derivative is used in rocket fuels, is produced by '
                'bubbling ammonia through a sodium hypochlorite solution?',
           'a': 'HYDRAZINE'},
          {'q': 'CHEMISTRY Short Answer: The isomerization reaction of a particular cis-alkene to its trans-isomer is '
                'first order. In terms of liters, moles, and seconds, what are the units for the rate constant of this '
                'reaction?',
           'a': 'INVERSE SECONDS'},
          {'q': 'CHEMISTRY Multiple Choice: For a given redox [REE-dox] reaction, which of the following pairs of '
                'thermodynamic statements is NOT possible?\n'
                'W) K-equilibium greater than 1 and delta-H greater than zero\n'
                'X) E-cell greater than zero and delta-G greater than zero\n'
                'Y) delta-H greater than zero and delta-G greater than zero\n'
                'Z) K-equilibium greater than 1 and E-cell greater than zero',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: How many total nodes exist within the highest energy pi molecular orbital for '
                '1,3-butadiene [One three byoo-tah-DYE-een]?',
           'a': '4'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds that can crystallize as network '
                'solids:\n'
                '1) Carbon dioxide; 2) Silicon dioxide; 3) Silicon carbide.',
           'a': '2 AND 3'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three reactions in terms of increasing delta H, from most '
                'negative to most positive: 1) Combustion of one mole of formaldehyde; 2) Combustion of one mole of '
                'methanol; 3) Combustion of one mole of methane.',
           'a': '3, 2, 1'},
          {'q': 'CHEMISTRY Multiple Choice: What element has the highest ionization energy?\n'
                'W) Hydrogen\n'
                'X) Helium\n'
                'Y) Lithium\n'
                'Z) Beryllium',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following compounds has the highest polarity?\n'
                'W) Carbon tetrachloride\n'
                'X) Dimethyl [dye-meth-il] ether [EE-thur]\n'
                'Y) Boron trifluoride [tri-FLOOR-ide]\n'
                'Z) Trinitrotoluene [try-nitro-TAWL-yoo-een]',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three ions in terms of increasing radius:\n'
                '1) Na+ [N A plus]; 2) Be2+ [B E plus two]; 3) Li+ [L I plus].',
           'a': '2, 3, 1'},
          {'q': 'CHEMISTRY Short Answer: What allotrope of phosphorus, which can be prepared by heating white '
                'phosphorus to\n'
                '300 degrees Celsius in the absence of air, is composed of amorphous interlocking P4 tetrahedra?',
           'a': 'RED PHOSPHORUS'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements best explains why chloroacetic '
                '[kloro-ah-SEE-tik] acid is a stronger acid than acetic [ah-SEE-tik] acid?\n'
                'W) Resonance delocalization of the conjugate base chloroacetate\n'
                'X) Withdrawal of electron density by chlorine\n'
                'Y) Donation of electron density by chlorine\n'
                'Z) Greater electronegativity of chlorine than oxygen',
           'a': 'X'},
          {'q': "CHEMISTRY Short Answer: What is the name for the wavelength at which a sample's absorbance does not "
                'change during a reaction?',
           'a': 'ISOSBESTIC POINT'},
          {'q': 'CHEMISTRY Short Answer: For the tri-iodide ion, what is the hybridization of the central iodine atom?',
           'a': 'DSP3'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds with dsp3 hybridized central '
                'atoms:\n'
                '1) Silicon tetrafluoride [tetrah-FLOOR-ide]; 2) Sulfur hexafluoride [hex-ah-FLOOR-ide]; 3) Sulfur '
                'tetrafluoride.',
           'a': '3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is an example of an ionic compound?\n'
                'W) Methane\n'
                'X) Chlorine dioxide\n'
                'Y) Dinitrogen trioxide\n'
                'Z) Calcium sulfide',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: What is the geometry of sulfur tetrafluoride [tetrah-FLOOR-ide]?',
           'a': 'SEESAW'},
          {'q': 'CHEMISTRY Short Answer: What quantity, in milliliters, of a 0.5 molar solution of sulfuric acid would '
                'be required to neutralize 30 mL of a 0.1 molar solution of sodium hydroxide?',
           'a': '3'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are TRUE of ideal '
                'concentration cells:\n'
                '1) They obey the Nernst equation; 2) At equilibrium, they have a positive redox [REE-dox] potential; '
                '3) They have a positive standard redox potential.',
           'a': '1'},
          {'q': 'CHEMISTRY Multiple Choice: Consider the reaction of two moles of hydrogen gas and one mole of oxygen '
                'gas to generate two moles of steam. Which of the following statements is TRUE?\n'
                'W) Delta H is greater than delta U\n'
                'X) Delta H is less than delta U\n'
                'Y) Delta H is equal to delta U\n'
                'Z) Delta H is greater than delta U at high temperatures, but less at low temperatures',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three diatomic [dye-ah-TOM-ik] molecules that '
                'MO theory predicts to be stable: 1) Li ; 2) Be ; 3) B .\n'
                '2 2 2',
           'a': '1 AND 3'},
          {'q': 'CHEMISTRY Short Answer: The hormone estrogen contains five stereocenters. How many stereoisomers of '
                'estrogen are possible?',
           'a': '32'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three techniques that could separate '
                'enantiomers [en-AN- tee-oh-mirz] in a racemic [ray-SEEM-ik] mixture of a chiral amine [KYE-ruhl '
                'ah-MEEN]: 1) Chiral chromatography\n'
                '[crow-mah-TAW-grah-fee]; 2) Crystallization with acetic acid; 3) Crystallization with plus tartaric '
                'acid.',
           'a': '1 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is the correct definition of molality?\n'
                'W) Kilograms of solute per liter of solvent\n'
                'X) Moles of solute per liter of solution\n'
                'Y) Moles of solute per liter of solvent\n'
                'Z) Moles of solute per kilogram of solvent',
           'a': 'Z'},
          {'q': 'CHEMISTRY Multiple Choice: Plants grown with deuterated [DOO-tur-ated] water grow more slowly than '
                'those grown with non-deuterated water. This is thought to be an illustration of which of the '
                'following effects?\n'
                'W) Quantum Hall effect\n'
                'X) Magnetic isotope effect\n'
                'Y) Steric [steh-rik] isotope effect\n'
                'Z) Kinetic isotope effect',
           'a': 'Z'},
          {'q': 'CHEMISTRY Multiple Choice: A student obtained a low value when he attempted to measure the number of '
                'waters of hydration in a sample of calcium sulfate. Which of the following mistakes could lead to the '
                'erroneous result?\n'
                'W) The sample was not heated enough\n'
                'X) The sample was heated too much\n'
                'Y) A balance that gave uniformly high readings was used\n'
                'Z) A balance that gave uniformly low readings was used',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following elements possesses the largest first ionization '
                'energy?\n'
                'W) Fluorine [FLOOR-een]\n'
                'X) Neon\n'
                'Y) Calcium\n'
                'Z) Argon',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following electrons would be most effective at shielding the '
                'nuclear charge seen by a 3s electron in an aluminum atom?\n'
                'W) 1s\n'
                'X) 2s\n'
                'Y) 2p\n'
                'Z) 3s',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: If an organo-magnesium compound is reacted with formaldehyde '
                '[foor-MAL-dih-hide], which of the following will be formed?\n'
                'W) Ketone [KEE-tone]\n'
                'X) Imine [IH-meen]\n'
                'Y) Secondary alcohol\n'
                'Z) Primary alcohol',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: What type of bond, which also exists in the transition states of carbocation '
                'rearrangements, allows each boron atom to achieve an octet in the compound diborane?',
           'a': 'THREE-CENTER TWO-ELECTRON BOND'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three analytical techniques that could be used '
                'to detect the difference between two diastereomers [dye-ah-STARE-ee-oh-murz]: 1) X-ray '
                'crystallography [crystal-AW-graphy];\n'
                '2) NMR spectroscopy [spek-TRAW-scuh-pee]; 3) Mass spectrometry [spek-TRAW-metry].',
           'a': '1 AND 2'},
          {'q': 'CHEMISTRY Multiple Choice: Trans fats necessarily contain what functional group?\n'
                'W) Ester\n'
                'X) Alkene\n'
                'Y) Alcohol\n'
                'Z) Amine [ah-MEEN]',
           'a': 'X'},
          {'q': "CHEMISTRY Multiple Choice: Tollens' test can detect aldehyde [AL-deh-hide]-containing compounds. To "
                'perform\n'
                "Tollens' test, an organic compound is mixed with a solution of silver ions. Which of the following "
                'indicates that the compound of interest contains an aldehyde?\n'
                'W) A silver mirror is formed\n'
                'X) Insoluble silver oxide precipitates from solution\n'
                'Y) The reaction mixture turns yellow\n'
                'Z) The aldehyde is reduced to an alcohol',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Consider ice at 0 degrees Celsius that is heated until it becomes water at '
                '80 degrees\n'
                'Celsius. Which of the following statements is TRUE concerning its volume?\n'
                'W) It monotonically [mono-TAWN-ik-lee] decreases\n'
                'X) It decreases until 4 degrees Celsius, then increases\n'
                'Y) It increases until 4 degrees Celsius, then remains constant\n'
                'Z) It remains constant',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following transition metal 2+ ions is most commonly found in '
                'a square planar geometry?\n'
                'W) Copper\n'
                'X) Nickel\n'
                'Y) Iron\n'
                'Z) Cobalt',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements is NOT true concerning the hydrogen '
                'atom, if only gross structure contributions are accounted for?\n'
                'W) 4s orbitals are at a higher energy than 3d orbitals\n'
                'X) 4d orbitals are at a higher energy than 3d orbitals\n'
                'Y) A 2p to 1s transition is more energetic than a 4p to 2s transition\n'
                'Z) The Balmer series includes only transitions to n=2',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three diatomic [dye-ah-TOM-ik] compounds that '
                'MO theory predicts to be paramagnetic: 1) B ; 2) C ; 3) N .\n'
                '2 2 2',
           'a': '1'},
          {'q': 'CHEMISTRY Short Answer: Rank the pH of the following three solutions, from lowest to highest: 1) One '
                'molar solution of hydrochloric acid; 2) One molar solution of acetic acid; 3) One molar solution of '
                'ammonium perchlorate.',
           'a': '1, 2, 3'},
          {'q': 'CHEMISTRY Short Answer: Identfiy all of the following three molecules that are likely to act as '
                'electrophiles in a substitution reaction: 1) Ammonia; 2) Bromide; 3) Methyl bromide.',
           'a': '3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is the most plausible first step in the solvolysis '
                '[sawl-VAWL- eh-sis] of tert-butyl [turt-BYU-til] iodide in water?\n'
                'W) Concerted substitution\n'
                'X) Attack of water to form a pentavalent [penta-VAY-lent] intermediate\n'
                'Y) Decomposition to form positively-charged intermediate\n'
                'Z) Decomposition to form negatively-charged intermediate',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three acids in terms of increasing pKa: 1) Chlorous '
                '[KLOR-us] acid;\n'
                '2) Hydroiodic [HIGH-droh-eye-AW-dik] acid; 3) Acetic [ah-SEE-tik] acid.',
           'a': '2, 1, 3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following compounds has the lowest boiling point?\n'
                'W) Water\n'
                'X) Hydrogen sulfide\n'
                'Y) Hydrogen selenide [SELL-en-ide]\n'
                'Z) Hydrogen telluride [TELL-ur-ide]',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are TRUE of the Nernst '
                'equation:\n'
                '1) The equation does not use the Faraday constant; 2) The standard redox [REE-dox] potential for a '
                'concentration cell is negative; 3) The Nernst equation accounts for overpotential.',
           'a': 'NONE OF THEM'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following titrations would have an equivalence point with a '
                'pH closest to 9?\n'
                'W) Titration of sodium hydroxide with hydrochloric acid\n'
                'X) Titration of hydrochloric acid with ammonia\n'
                'Y) Titration of acetic acid with sodium hydroxide\n'
                'Z) Titration of barium hydroxide with sulfuric acid',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are TRUE of the '
                'permanganate [pur-MAYNG-en-ate] ion: 1) It is reduced to Mn2+ in neutral solution; 2) It contains '
                'manganese [MAYN-gan-eez]in the +7 oxidation state; 3) It can be used as an indicator and titrant '
                '[TIE-trant] in a potentiometric [poh-ten-shee-oh-MEH-tric] titration [tie-TRAY-shun].',
           'a': '2 AND 3'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds that are a stronger base than '
                'sodium hydride: 1) T-butyl [t-byu-til] lithium; 2) Ammonia; 3) Sodium tert-butoxide '
                '[tert-byu-tox-eyed].',
           'a': 'JUST 1'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds that are most likely to undergo '
                'electrophilic [ee-lektroh-FILL-ik] aromatic substitution at the meta position: 1) Nitrobenzene;\n'
                '2) Toluene [TAWL-you-een]; 3) Ethyl benzoate [BEN-zoh-ate].',
           'a': '1 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements concerning crystal structure is NOT '
                'true?\n'
                'W) HCP lattices are more space-filling than FCC lattices\n'
                'X) Cesium [SEEZ-ee-um] chloride lattices form when anions [AN-eye-ons] and cations [CAT-eye-onz] are '
                'of roughly equal size\n'
                'Y) Rock-salt lattices have (6,6)-coordination\n'
                'Z) The crystal structure of a metal is dependent on pressure and temperature',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following four species that have a square planar '
                'geometry:\n'
                '1) Sulfur tetrafluoride [tetrah-FLOOR-ide]; 2) Carbon tetrachloride [tetrah-KLOOR-ide]; 3) Xenon '
                '[ZEE-non] tetrafluoride; 4) Iodine tetrabromide [tetrah-BROH-mide] anion [AN-eye-on] with a 1– charge',
           'a': '3 AND 4'},
          {'q': 'CHEMISTRY Multiple Choice: Consider the gas-phase decomposition of PCl 5 into PCl 3 and Cl 2 . If the '
                'reaction begins with 5 atmospheres of PCl , and if the partial pressure of chlorine is x atm at '
                'equilibrium, which of the following\n'
                '5 expressions for Kp is correct?\n'
                'W) The fraction with numerator x and denominator 5 minus x\n'
                'X) The fraction with numerator x and denominator open parenthesis 5 minus x close parenthesis '
                'squared\n'
                'Y) The fraction with numerator x squared and denominator 5 minus x\n'
                'Z) The fraction with numerator x squared and denominator open parenthesis 5 minus x close parenthesis '
                'squared',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: What is the name of the analytic method in chemistry that uses the spin-flip '
                'transitions of nuclei to identify the unique electronic bonding environments for a given compound?',
           'a': 'NMR'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following compounds has the highest vapor pressure at 25 '
                'degrees\n'
                'Celsius?\n'
                'W) Water\n'
                'X) Ethanol\n'
                'Y) Methanol\n'
                'Z) Diethyl [dye-eh-thyl] ether [EE-thur]',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: Consider the heating of anhydrous [an-HIGH-drus] solid calcium carbonate to '
                'form gaseous CO and solid calcium oxide. Identify all of the following three changes that would shift '
                'this reaction to the right:\n'
                '2\n'
                '1) Adding more calcium carbonate; 2) Adding more calcium oxide; 3) Increasing the temperature.',
           'a': '3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following correctly explains why oxygen exists in a '
                'double-bonded diatomic [dye-ah-TOM-ik] form whereas sulfur forms S8 chains?\n'
                'W) Sulfur is too electropositive to form strong pi [pie] bonds\n'
                "X) Sulfur's 3p orbitals have less overlap for pi bonding\n"
                'Y) Oxygen is paramagnetic whereas sulfur is diamagnetic [dye-ah-mag-NET-ik]\n'
                'Z) Sulfur can expand its valence [VAY-lense] shell to hold more than eight electrons',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are TRUE concerning '
                'carbon monoxide: 1) It is a high-field ligand [LIH-gund]; 2) It often forms complexes with neutral '
                'metal atoms; 3) It is a pi [pie] donor ligand.',
           'a': '1'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three quantites in reaction kinetics that are '
                'dimensionless:\n'
                '1) Rate constant; 2) Steric [steh-rik] factor; 3) Collision frequency.',
           'a': '2'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three changes that would shift the equilibrium '
                'of the Haber\n'
                '[HAH-bur] process to the right: 1) Adding hydrogen gas; 2) Adding an inert gas; 3) Increasing the '
                'volume of the container at constant temperature.',
           'a': '1 ONLY'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements is TRUE concerning SN 2 reactions?\n'
                'W) Pentavalent [penta-vay-lent] transition state\n'
                'X) Pentavalent intermediate\n'
                'Y) Trivalent [try-vay-lent] transition state\n'
                'Z) Trivalent intermediate',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements concerning crystal structures '
                'that are true:\n'
                '1) The FCC lattice fills volume more efficiently than the BCC lattice; 2) The number of atoms in a '
                'BCC unit cell is 4;\n'
                '3) The coordination number of an FCC lattice is 12.',
           'a': '1 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following compounds would have the largest retention factor '
                'in a TLC experiment with a silica stationary phase and hexane mobile phase?\n'
                'W) Benzene\n'
                'X) Benzoic acid [ben-ZOH-ik]\n'
                'Y) Phenylacetone [fennel-ASS-eh-tone]\n'
                'Z) Benzyl [BEN-zil] methyl ether',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Arrange the following three hydrogens in a proton-NMR spectrum in terms of '
                'increasing chemical shift: 1) Hydrogens in benzene; 2) Aldehyde hydrogen in acetaldehyde '
                '[asset-AL-de-hide];\n'
                '3) Hydroxyl [high-DROX-il] group in methanol.',
           'a': '3, 1, 2'},
          {'q': 'CHEMISTRY Short Answer: What is the empirical formula for the acid anhydride of phosphoric '
                '[faws-FOR-ik] acid?',
           'a': 'P2O5'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following four compounds in which London dispersion '
                'forces dominate intermolecular interactions: 1) Dichloromethane; 2) Neon; 3) Ammonia; 4) Hydrogen.',
           'a': '2 AND 4'},
          {'q': 'CHEMISTRY Short Answer: What is the major acidic species that forms when an acid is dissolved in '
                'water?',
           'a': 'HYDRONIUM'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds that have a higher lattice '
                'energy than sodium fluoride: 1) Sodium chloride; 2) Aluminum fluoride; 3) Sodium oxide.',
           'a': '2 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: An alkyne[AL-kine] is added to a reaction vessel containing pressurized '
                'hydrogen gas and a catalyst consisting of palladium [pah-LAID-ee-um] poisoned by traces of lead(II) '
                'ions and quinoline [KWIN-oh- lin]. Which of the following is the major product of this reaction?\n'
                'W) Alkane\n'
                'X) Cis-alkene [sis-al-KEEN\n'
                'Y) Trans-alkene\n'
                'Z) Alcohol',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are true concerning '
                'elimination reactions: 1) E2 is a concerted reaction; 2) E1 is substantially accelerated by strong, '
                'unhindered bases; 3) Cis-alkenes are often thermodynamically preferred to trans-alkenes.',
           'a': '1'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following methods is LEAST helpful in identifying chiral '
                '[KYE-ruhl] isomers?\n'
                'W) X-ray diffraction\n'
                'X) Quadrupole [QUAD-roo-pole] mass spectrometry [spek-TRAW-metry]\n'
                'Y) Nuclear magnetic resonance spectroscopy [spek-TRAW-scuh-pee]\n'
                'Z) Raman [RAH-min] spectroscopy',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are true of a mixture of '
                '96% ethanol and 4% water: 1) The boiling point of the mixture is greater than that of either pure '
                'ethanol or pure water; 2) The components can be separated by fractional distillation; 3) The mixture '
                'deviates from Raoult’s [rah-OOLZ] law.',
           'a': '3'},
          {'q': 'CHEMISTRY Short Answer: Porphyrin [POOR-feh-rin] is a chelating [KEY-lay-ting] ligand [LIH-gund]. How '
                'many bonds can it form to a metal center?',
           'a': '4'},
          {'q': 'CHEMISTRY Short Answer: Rank the following four compounds in terms of increasing net dipole moment:\n'
                '1) Carbon dioxide; 2) Hydrogen chloride; 3) Hydrogen fluoride; 4) Carbon monoxide.',
           'a': '1, 4, 2, 3'},
          {'q': 'CHEMISTRY Short Answer: Acetylene has a pKa of 25, while hydroxide ions have a pKa of about 16. '
                'Expressing your answer to the nearest power of 10, if they were mixed in equimolar amounts, one in '
                'how many molecules of acetylene would be deprotonated?',
           'a': '9'},
          {'q': 'CHEMISTRY Short Answer: How many unpaired electrons does high-spin open bracket CoF 6 close bracket '
                'to the 3 negative have?',
           'a': '4'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following ligands induces the largest electronic d orbital '
                'splitting in a transition metal complex?\n'
                'W) Chloro\n'
                'X) Aqua\n'
                'Y) Cyano\n'
                'Z) Ethylenediamine',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Consider an organic compound with no rings in its structure, and with the '
                'chemical formula C 12 H 16 O 2 [C twelve H sixteen O two]. What is the number of double bonds in its '
                'structure?',
           'a': '5'},
          {'q': 'CHEMISTRY Multiple Choice: Consider the hypothetical reaction 2A, aqueous, plus 2B, gaseous, yields '
                '3C, aqueous, plus D, gaseous,where the change in enthalpy of the reaction is -22 kilojoules. Which of '
                'the following will drive the reaction toward the products?\n'
                'W) Increasing the temperature\n'
                'X) Increasing the volume of the reaction vessel at constant temperature\n'
                'Y) Increasing the pressure\n'
                'Z) Increasing the amount of D',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following solvents would most accelerate an SN2 reaction?\n'
                'W) Hexane\n'
                'X) Dichloromethane\n'
                'Y) DMSO\n'
                'Z) Ethyl acetate',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three elements in terms of increasing electron affinities: '
                '1) Carbon;\n'
                '2) Nitrogen; 3) Oxygen.',
           'a': '2, 1, 3'},
          {'q': 'CHEMISTRY Short Answer: What effect, which applies to the chemistry of real gases and is exploited in '
                "the liquefaction of air, causes a gas's temperature to decrease in an adiabatic [ad-ee-ah-BAT-ik] "
                'isenthalpic expansion?',
           'a': 'JOULE-THOMSON EFFECT'},
          {'q': 'CHEMISTRY Short Answer: What is the IUPAC name for the cyclic saturated hydrocarbon containing four '
                'carbon atoms?',
           'a': 'CYCLOBUTANE'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three functional groups that commonly '
                'participate in addition reactions: 1) Aldehyde [AL-deh-hide]; 2) Alkene ; 3) Alkyl [AL-kil] halide '
                '[HAY-lide].',
           'a': '1 AND 2'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is not true about early transition metals in '
                'comparison to late transition metals?\n'
                'W) Easier to oxidize\n'
                'X) More electropositive\n'
                'Y) Higher oxidation states\n'
                'Z) Larger radii',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three hydrogen atoms in terms of increasing pKa: 1) '
                'Hydrogen atom in a water molecule; 2) Hydrogen atom in acetylene [ah-SET-ihl-een]; 3) Hydroxyl '
                '[high-DROX-il] hydrogen atom in t-butyl [t-BYU-til] alcohol.',
           'a': '1, 3, 2'},
          {'q': 'CHEMISTRY Short Answer: Consider a single-reactant reaction that has a rate constant equal to 24 '
                'seconds to the negative 1, molar to the negative 2. What is the order of this reaction?',
           'a': '3'},
          {'q': 'CHEMISTRY Short Answer: The Heck coupling is a cross-coupling reaction that treats an aryl halide '
                'with what functional group?',
           'a': 'ALKENE'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three species that are Lewis acids:\n'
                '1) Zn2+; 2) Cl- ; 3) BH .\n'
                '3',
           'a': '1 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements about a valid wave function is true?\n'
                'W) A wave function must be single-valued\n'
                'X) A wave function must approach infinity as r approaches zero\n'
                'Y) The spatial integral of wave functions for different orbitals in an atom must be one\n'
                'Z) The integral of the wave function times its own complex conjugate must equal zero',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: What is the bond-order of an oxygen-oxygen bond in ozone?', 'a': '1.5'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are true regarding atomic '
                'nuclei:\n'
                '1) The maximum number of protons in a stable nucleus is 92; 2) Nuclei with excess neutrons become '
                'more stable through beta emission; 3) Nuclei with excess protons can become more stable through '
                'electron capture.',
           'a': '2 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following molecular geometries can exhibit meridional '
                'isomerism?\n'
                'W) Linear\n'
                'X) Square planar\n'
                'Y) Tetrahedral\n'
                'Z) Octahedral',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: What is the fewest number of carbonyl [carbon-EEL] stretching bands that can '
                'be seen in the infrared spectrum of a metal atom that is bound to four CO ligands [LIH-gunz]?',
           'a': '1'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three fatty acids that are unsaturated: 1) C 13 '
                'H 27 COOH;\n'
                '2) C H COOH; 3) C H COOH.\n'
                '17 35 16 29',
           'a': 'JUST 3'},
          {'q': 'CHEMISTRY Short Answer: What reaction in organic chemistry forms alkenes via a reaction of a carbonyl '
                '[carbon-EEL] group with a yellow-colored phosphorous ylide [ILL-id]?',
           'a': 'WITTIG REACTION'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following four compounds that are polar:\n'
                '1) XeF ; 2) SF ; 3) BrF ; 4) PF .\n'
                '4 4 5 5',
           'a': '2 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is NOT one of the seven crystal lattice systems?\n'
                'W) Orthorhombic\n'
                'X) Monoclinic\n'
                'Y) Octagonal\n'
                'Z) Cubic',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Within a valence bond interpretation, what is the hybridization of the carbon '
                'atoms’ valence electrons in the ethylene molecule?',
           'a': 'SP2'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following elements has an electron configuration that follows '
                'the simple order of orbital filling?\n'
                'W) Technetium [tek-NEE-shee-um]\n'
                'X) Ruthenium [roo-THEE-nee-um]\n'
                'Y) Rhodium\n'
                'Z) Palladium [pah-LAID-ee-um]',
           'a': 'W'}, {'q': 'CHEMISTRY Short Answer: Given the percentages by mass of different elements in a compound, identify '
                'all of the following three characteristics of the compound that can be uniquely determined:1) The '
                'empirical formula; 2) The molecular formula; 3) The structure',
           'a': '1'},
          {'q': 'CHEMISTRY Short Answer: What property of an element is defined as the amount of energy released when '
                'one mole of electrons is added to one mole of the neutral atomic element in the gaseous state?',
           'a': 'ELECTRON AFFINITY'},
          {'q': 'CHEMISTRY Multiple Choice: A molecule with the molecular formula C H cannot form\n'
                '5 12 which of the following structural orientations?\n'
                'W) Straight-chain alkane\n'
                'X) Branched alkane\n'
                'Y) Cycloalkane\n'
                'Z) Normal alkane',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: In the balanced equation for the combustion of octane, what are the '
                'coefficients for carbon dioxide and water respectively?',
           'a': '16; 18'},
          {'q': 'CHEMISTRY Short Answer: What principle of chemical equilibrium states that if a chemical system at '
                'equilibrium experiences a change in concentration, temperature, or pressure, the equilibrium will '
                'shift in order to counteract that change?',
           'a': 'LE CHATELIER’S PRINCIPLE'},
          {'q': 'CHEMISTRY Multiple Choice: Consider both the hydrogenation [high-draw-jen-AY-shun] and the '
                'bromination [broh-min-AY-shun] of alkenes using elemental bromine. Which of the following statements '
                'concerning these reactions is TRUE?\n'
                'W) Both reactions are syn-additions\n'
                'X) Hydrogenation is a syn-addition, but bromination is an anti-addition\n'
                'Y) Hydrogenation is an anti-addition, but bromination is a syn-addition\n'
                'Z) Both reactions are anti-additions',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: One confirmed transformation of ununoctium [un-un-AWK- tee-um] is the decay '
                'of ununoctium-294 into livermorium [liver-MOOR-ee-um]-290. What type of decay process is this?',
           'a': 'ALPHA DECAY'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following IR spectrum wavenumber ranges are characteristic of '
                'alcohols, terminal alkynes, and amines?\n'
                'W) 3700 – 3200\n'
                'X) 3200 – 2700\n'
                'Y) 2300 – 2100\n'
                'Z) 1750 – 1650',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: In dilute aqueous solution, H SO is classified as which of\n'
                '2 4 the following?\n'
                'W) Strong acid\n'
                'X) Weak acid\n'
                'Y) Strong base\n'
                'Z) Weak base',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: What signs for enthalpy and entropy changes, respectively, guarantee a '
                'spontaneous reaction at all temperatures?\n'
                'W) Positive, positive\n'
                'X) Positive, negative\n'
                'Y) Negative, positive\n'
                'Z) Negative, negative',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following functional groups is most likely to be formed when '
                'dodecane [doh-DECK-ane] undergoes "cracking?"\n'
                'W) Alcohol\n'
                'X) Aldehyde\n'
                'Y) Alkene\n'
                'Z) Amide',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: In diagrams of reaction mechanisms, the standard double- headed curved arrow '
                'represents the movement of what entities?',
           'a': 'ELECTRONS'},
          {'q': 'CHEMISTRY Short Answer: What property of concentration in chemistry is defined as moles of solute per '
                'kilograms of solvent and is useful when calculating freezing-point depression and boiling-point '
                'elevation?',
           'a': 'MOLALITY'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following substances would you expect to be the most miscible '
                'with water?\n'
                'W) Methanol\n'
                'X) Ethyl acetate\n'
                'Y) 2-butanal\n'
                'Z) Butyraldehyde',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: If an acid is added to an unbuffered, neutral aqueous solution, which of '
                'the following is true?\n'
                'W) The hydroxide ion concentration increases\n'
                'X) The hydronium ion concentration decreases\n'
                'Y) The hydroxide ion concentration decreases\n'
                'Z) The concentrations of the hydronium and hydroxide ion concentrations remain unchanged',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: A student performs combustion analysis on a compound composed of carbon, '
                'hydrogen, oxygen, and possibly nitrogen - with molecular mass 56 grams per mole. One mole of the '
                'compound reacts with 3 moles of oxygen gas to generate 2 moles of carbon dioxide, 1 mole of water, '
                'and an unknown product. How many nitrogen atoms are in the chemical formula?\n'
                'W) Zero\n'
                'X) One\n'
                'Y) Two\n'
                'Z) Three',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: At what temperature, in degrees Celsius, does the change in enthalpy for the '
                'oxidation of 1 mole of graphite under 1 atmosphere of oxygen to generate carbon dioxide exactly equal '
                'the standard enthalpy of formation of carbon dioxide?',
           'a': '25'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds that have sp2 [S-P-2] '
                'hybridized central atoms: 1) Nitrogen trichloride; 2) Carbon dioxide; 3) Hydrocyanic acid.',
           'a': 'NONE OF THEM'},
          {'q': 'CHEMISTRY Multiple Choice: Many salts dissolve to a greater extent in hot water than cold water. '
                'Which of the following best explains this fact?\n'
                'W) Most salts dissolve endothermically\n'
                'X) Most salts dissolve exothermically\n'
                'Y) There are more collisions between salt ions and water molecules at a higher temperature\n'
                'Z) The ion-dipole forces between water molecules and salt ions increase with temperature',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: A protein chemist isolates a new enzyme. Which of the following '
                'techniques, when performed alone, would be most useful for determining its size?\n'
                'W) NMR spectroscopy\n'
                'X) MALDI-TOF mass spectrometry\n'
                'Y) Elemental analysis\n'
                'Z) Gravimetric analysis',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: An aqueous solution contains silver ions, barium ions, iron (III) ions, '
                'and nitrate ions. Upon addition of sodium chloride, which of the following will precipitate out of '
                'the solution first?\n'
                'W) Iron (III) chloride\n'
                'X) Barium chloride\n'
                'Y) Sodium nitrate\n'
                'Z) Silver chloride',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: Other than hydrogen and the noble elementsWhat non-noble element has the '
                'lowest energy valence orbitals?',
           'a': 'FLUORINE'},
          {'q': 'CHEMISTRY Multiple Choice: O and O are considered what type of molecules?\n'
                '2 3\n'
                'W) Allotropes\n'
                'X) Structural isomers\n'
                'Y) Isotopes\n'
                'Z) Geometrical isomers',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: If we assume that the bond order in carbon monoxide is three, which of the '
                'following correctly gives the formal charges on carbon and oxygen?\n'
                'W) 0 on both carbon and oxygen\n'
                'X) +1 on carbon and -1 on oxygen\n'
                'Y) -1 on carbon and +1 on oxygen\n'
                'Z) +2 on carbon and -2 on oxygen',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Part of the reason that graphene demonstrates such high mechanical strength '
                'is that the carbon atoms are in what hybridization state?',
           'a': 'SP2'},
          {'q': 'CHEMISTRY Short Answer: Order the following three gases from slowest to fastest in terms of their '
                'rate of effusion at 25 degrees Celcius: 1) Helium; 2) Argon; 3) Neon.',
           'a': '2, 3, 1'},
          {'q': 'CHEMISTRY Multiple Choice: The bond angle in NH is closest to which of the following\n'
                '3 degree values?\n'
                'W) 90\n'
                'X) 110\n'
                'Y) 120\n'
                'Z) 180',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: D orbitals can overlap to form sigma, pi, or delta bonds. Which of these '
                'types of d-d bonds is strongest?\n'
                'W) Sigma\n'
                'X) Pi\n'
                'Y) Delta\n'
                'Z) They are equally strong',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: An atom is sp3 [S-P-3] hybridized. Which of the following is\n'
                'NOT a possible molecular geometry about this atom?\n'
                'W) Bent\n'
                'X) Trigonal pyramidal\n'
                'Y) Tetrahedral\n'
                'Z) Trigonal bipyramidal',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: What region of the electromagnetic spectrum would be able to excite an '
                'electron from a 1s orbital to a 2p orbital in a helium atom?',
           'a': 'ULTRAVIOLET'},
          {'q': 'CHEMISTRY Short Answer: What is the name of the oxyanion [ox-ee-AN-eye-on] of bromine in which '
                'bromine has a +7 oxidation state and formula BrO - [B-R-oh-4-negative]?\n'
                '4',
           'a': 'PERBROMATE'},
          {'q': 'CHEMISTRY Multiple Choice: The functional groups forming a peptide bond do NOT contain which of the '
                'following atoms?\n'
                'W) Hydrogen\n'
                'X) Nitrogen\n'
                'Y) Oxygen\n'
                'Z) Phosphorus',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: What alcohol reactant is needed to perform a Fischer esterification on a '
                'carboxylic acid to yield a methyl ester?',
           'a': 'METHANOL'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three acid solutions from lowest pH to highest pH:\n'
                '1) 1.0 normal sulfuric acid; 2) 1.0 molal sulfuric acid; 3) 1.0 molar sulfuric acid.',
           'a': '3, 2, 1'},
          {'q': 'CHEMISTRY Multiple Choice: Nitrogen monoxide is an example of which of the following?\n'
                'W) An expanded octet\n'
                'X) A resonance molecule\n'
                'Y) A dimerizing molecule\n'
                'Z) A free radical',
           'a': 'Z'},
          {'q': 'CHEMISTRY Multiple Choice: M2+ is a metal ion with a ground state electron configuration of '
                '[Ar]3d84s0 [argon-3-d-8-4-s-0]. What is the identity of M?\n'
                'W) Molybdenum [muh-LIB-den-um]\n'
                'X) Nickel\n'
                'Y) Niobium\n'
                'Z) Magnesium',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: What is the coordination number of a body-centered cubic lattice?\n'
                'W) 2\n'
                'X) 4\n'
                'Y) 6\n'
                'Z) 8',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: What quantum number determines if an orbital is s, p, d, or f?',
           'a': 'AZIMUTHAL'},
          {'q': 'CHEMISTRY Multiple Choice: What is the maximum number of electrons that the 3d level can hold?\n'
                'W) 2\n'
                'X) 6\n'
                'Y) 10\n'
                'Z) 14',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: Under aqueous conditions, which of the following reactions would generate '
                'a precipitate?\n'
                'W) Ammonium chloride mixed with potassium hydroxide\n'
                'X) Calcium chloride mixed with potassium nitrate\n'
                'Y) Calcium carbonate mixed with hydrochloric acid\n'
                'Z) Barium chloride mixed with potassium sulfate',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: The +3 oxide of what element is added to molten silicate to generate a glass '
                'with a low thermal expansion coefficient that is used for lab glassware?',
           'a': 'BORON'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three gaseous phase monatomic elements in ascending order '
                'of electron affinity: 1) Boron; 2) Silicon; 3) Chlorine.',
           'a': '1, 2, 3'},
          {'q': 'CHEMISTRY Multiple Choice: Under which of the following conditions does the behavior of real gases '
                'deviate most from that predicted by the Ideal Gas Law?\n'
                'W) Low pressure, low temperature\n'
                'X) High pressure, low temperature\n'
                'Y) Low pressure, high temperature\n'
                'Z) High pressure, high temperature',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following best explains why NaCl has a higher melting point '
                'than HCl?\n'
                'W) HCl can form hydrogen bonds, while NaCl cannot\n'
                'X) HCl has stronger London dispersion forces\n'
                'Y) HCl is a molecular compound, while NaCl is an ionic compound\n'
                'Z) HCl is a network compound, while NaCl is a molecular compound',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: Which type of hybridization is found in the central atom of carbon '
                'dioxide?\n'
                'W) sp [s-p]\n'
                'X) sp2 [s-p-2]\n'
                'Y) sp3 [s-p-3]\n'
                'Z) sp4 [s-p-4]',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: What type of fluid undergoes large changes in density in response to small '
                'changes in pressure and temperature, and can be formed by heating carbon dioxide above\n'
                '31 degrees Celsius at pressures above 72.8 atmospheres?',
           'a': 'SUPERCRITICAL FLUID'},
          {'q': 'CHEMISTRY Short Answer: What is the only alkali metal that forms a stable nitride at room temperature '
                'and standard pressure?',
           'a': 'LITHIUM'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following biological macromolecules does NOT contain '
                'nitrogen?\n'
                'W) DNA\n'
                'X) RNA\n'
                'Y) Insulin\n'
                'Z) Amylose [AM-il-ohse]',
           'a': 'Z'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following atoms has at least one completely filled p- '
                'subshell?\n'
                'W) Sulfur\n'
                'X) Oxygen\n'
                'Y) Boron\n'
                'Z) Helium',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: The industrial production of ammonia involves a reaction that combines what '
                'two gases?',
           'a': 'NITROGEN AND HYDROGEN'},
          {'q': 'CHEMISTRY Multiple Choice: What type of magnetism opposes an applied magnetic field and is dominant '
                'in materials with no unpaired electrons?\n'
                'W) Diamagnetism\n'
                'X) Paramagnetism\n'
                'Y) Ferromagnetism\n'
                'Z) Antiferromagnetism',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is most likely to form hydrogen bonds?\n'
                'W) HI\n'
                'X) HNO – [H-N-O-2-negative]\n'
                'Y) C H\n'
                'Z) HCl',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following bonds has the shortest bond length?\n'
                'W) H-F\n'
                'X) H-Cl\n'
                'Y) H-Br\n'
                'Z) H-I',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: What is the name for the constant, approximately 1.4 times 10-23 joules per '
                'kelvin, that sets an energy scale for a system at a particular temperature, and is equal to the ideal '
                'gas constant over Avogadro’s number?',
           'a': 'BOLTZMANN CONSTANT'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following compounds does NOT have an adequate '
                'octet-rule-satisfying Lewis structure representation?\n'
                'W) Nitrogen dioxide\n'
                'X) Sulfur dioxide\n'
                'Y) Carbon dioxide\n'
                'Z) Oxygen difluoride',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following types of hydrocarbons are saturated?\n'
                'W) Alkanes\n'
                'X) Alkenes\n'
                'Y) Alkynes\n'
                'Z) Aromatic hydrocarbons',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: James Chadwick observed a type of radiation consisting of neutrally charged '
                'particles during his experiments with beryllium. What particles make up this radiation?',
           'a': 'NEUTRONS'},
          {'q': 'CHEMISTRY Short Answer: What compounds, examples of which include glyceraldehyde\n'
                '[glih-ser-AL-de-hide] and mannose, are formally polyhydroxy [polly-high-DROX-ee] ketones with '
                'empirical formula CH O and are the basic energy, storage, and structural molecules of life?\n'
                '2',
           'a': 'CARBOHYDRATES'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following molecules can exist in boat and chair '
                'configurations?\n'
                'W) Benzene\n'
                'X) Cyclohexane [sye-kloh-HEX-ane]\n'
                'Y) Cyclopentadiene [sye-kloh-penta-DYE-een]\n'
                'Z) Napthalene [NAP-thah-leen]',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following correctly explains why concentration cells have a '
                'standard cell potential of 0 volts?\n'
                'W) According to the Nernst equation, the standard cell potential is cancelled out by the '
                'concentration dependent term\n'
                'X) At standard conditions, all cells have a standard cell potential of 0 volts\n'
                'Y) Standard cell potentials are measured with all species at equal concentrations\n'
                'Z) Concentration cells are used as a standard, so their standard cell potential is arbitrarily set to '
                '0',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is an example of a molecular solid?\n'
                'W) Silicon\n'
                'X) Iodine\n'
                'Y) Diamond\n'
                'Z) Graphite',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: What organic functional group can be found at the N terminus of a protein and '
                'consists of a nitrogen atom bonded to one or more carbon atoms?',
           'a': 'AMINE'},
          {'q': 'CHEMISTRY Multiple Choice: An aqueous solution of sodium sulfate is electrolyzed using platinum '
                'electrodes. If phenolphthalein [fee-nawlf-THAY-leen] indicator is added to the solution, which of the '
                'following will be observed?\n'
                'W) The solution is colorless everywhere except at the cathode, where it is pink\n'
                'X) The solution is colorless everywhere except at the anode, where it is pink\n'
                'Y) The solution is pink everywhere except at the cathode, where it is colorless\n'
                'Z) The solution is pink everywhere except at the anode, where it is colorless',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Hydrogen peroxide is:\n'
                'W) Less dense than water and boils at a lower temperature\n'
                'X) Less dense than water and boils at a higher temperature\n'
                'Y) More dense than water and boils at a lower temperature\n'
                'Z) More dense than water and boils at a higher temperature',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three compounds that have only\n'
                'London dispersion forces operating between the molecules: 1) Difluoromethane [dye-floor-oh-\n'
                'MEH-thane]; 2) Hydrogen chloride; 3) Tetrachloromethane [tetrah-kloor-oh-MEH-thane].',
           'a': '3'},
          {'q': 'CHEMISTRY Multiple Choice: A scientist thinks she has found a sample of rock 10 billion years old, a '
                'leftover fragment from the formation of an early solar system. Which of the following parent '
                'isotope’s concentrations would be most useful in confirming this?\n'
                'W) Potassium-40\n'
                'X) Thorium-238\n'
                'Y) Uranium-234\n'
                'Z) Carbon-14',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following molecules is most polar?\n'
                'W) Ethane\n'
                'X) Carbon tetrachloride\n'
                'Y) Hexane\n'
                'Z) Pyridine',
           'a': 'Z'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following neutral ground state atoms has the lowest '
                'ionization energy?\n'
                'W) Carbon\n'
                'X) Boron\n'
                'Y) Nitrogen\n'
                'Z) Oxygen',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: The oxidation of elemental lithium with which of the following is a redox '
                'reaction that is MOST favorable?\n'
                'W) Fluorine gas\n'
                'X) Hydrogen gas\n'
                'Y) Iron (II)\n'
                'Z) Copper (I)',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements is NOT true regarding colligative '
                '[koh-LIG-ah-tiv] properties?\n'
                'W) They do not depend on the identity of the solute\n'
                "X) Sodium chloride has a van't Hoff factor less than one\n"
                'Y) The osmotic pressure of a solution increases with increasing solute concentration\n'
                'Z) The freezing point of a solution decreases with increasing solute concentration',
           'a': 'X'},
          {'q': 'CHEMISTRY Multiple Choice: Change in which of the following quantities must be positive for a '
                'spontaneous process?\n'
                'W) Gibbs free energy of the system\n'
                'X) Entropy of the system\n'
                'Y) Gibbs free energy of the universe\n'
                'Z) Entropy of the universe',
           'a': 'Z'},
          {'q': 'CHEMISTRY Multiple Choice: The reaction of hypochlorite and chloride ions in the presence of sulfuric '
                'acid generates gaseous chlorine endothermically in a closed vessel. Increasing which of the following '
                'would shift the reaction to the left?\n'
                'W) Volume\n'
                'X) Temperature\n'
                'Y) pH\n'
                'Z) Pressure of inert gas',
           'a': 'Y'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three metals that have soluble chlorides: 1) '
                'Silver; 2) Iron; 3) Zinc.',
           'a': '2 AND 3'},
          {'q': 'CHEMISTRY Multiple Choice: Consider the gas phase exothermic reaction of phosphorous trichloride '
                '[try-KLOOR-ide] with chlorine to yield phosphorous pentachloride. Under which of the following '
                'conditions is the equilibrium constant greater than one?\n'
                'W) At low temperatures\n'
                'X) At high temperatures\n'
                'Y) At all temperatures\n'
                'Z) It is never greater than one',
           'a': 'W'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements is NOT true regarding alloys?\n'
                'W) Alloys are generally more brittle than the metals from which they are made\n'
                'X) Alloys are generally harder than the metals from which they are made\n'
                'Y) Alloys are generally better electric conductors than the metals from which they are made\n'
                'Z) Alloys are generally worse thermal conductors than the metals from which they are made',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following techniques would be most useful for determining the '
                'change in enthalpy of a reaction?\n'
                'W) Visible light spectroscopy\n'
                'X) Calorimetry [cal-or-IH-metree]\n'
                'Y) Crystallography\n'
                'Z) Gravimetry [graa-VIH-metree]',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: A cylinder has an internal diameter of 3 centimeters and a piston is '
                'depressed 20 centimeters with a pressure of 2 atmospheres. Assuming that atmospheric pressure is 1 x '
                '105 pascals, to two significant figures and in joules, how much work is done during the compression?',
           'a': '28'},
          {'q': 'CHEMISTRY Short Answer: A 12.4 liter balloon is at 27 degrees Celsius. It is cooled at constant '
                'pressure to -23 degrees Celsius. To the nearest tenth and in liters, what is the final volume of the '
                'balloon?',
           'a': '10.3'},
          {'q': 'CHEMISTRY Short Answer: What allotrope of phosphorous is thermodynamically stable at room temperature '
                'and pressure and is structured as puckered sheets of linked atoms connected in 6- membered rings?',
           'a': 'BLACK PHOSPHORUS'},
          {'q': 'CHEMISTRY Short Answer: Titanium forms a non-stoichiometric oxide where there are 1.18 oxygen atoms '
                'per titanium atom. If the oxide contains Ti2+ and Ti3+ cations, what is the ratio of the\n'
                '2+ ion abundance to the 3+ ion abundance?',
           'a': '16/9'},
          {'q': 'CHEMISTRY Short Answer: What general type of bond is formed when two lobes of an orbital of one atom '
                'overlap two lobes of an orbital of the other atom?',
           'a': 'PI BOND'},
          {'q': 'CHEMISTRY Short Answer: A solution of weak acid that is 0.1 molar is 1% ionized at room temperature. '
                'To one significant figure, what is the acid’s pKa value?',
           'a': '5'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following values, in volts, is closest to the standard emf '
                '[E-M-F] produced by the Daniell cell?\n'
                'W) 0.6\n'
                'X) 0.8\n'
                'Y) 1.1\n'
                'Z) 1.5',
           'a': 'Y'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following functional groups undergoes a reaction with ozone '
                'to generate separate ketones or aldehydes, rapidly decolorizes bromine, and is generated by '
                'dehydration reactions?\n'
                'W) Alkene\n'
                'X) Ester\n'
                'Y) Alkane\n'
                'Z) Alcohol',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: By what process can a molecule in the singlet excited state relax to the '
                'ground state with concomitant [Kon-koh-MIT-ent] emission of light?',
           'a': 'FLUORESCENCE'},
          {'q': 'CHEMISTRY Short Answer: An SN1 reaction is performed by reacting sodium bromide with\n'
                '(S)-2-chlorobutane, and generates a 1 molar mixture of 70% (S)-2-bromobutane and 30% (R)-2- '
                'bromobutane. If the optical rotation of the solution was 9.2°, what is the optical rotation of pure '
                '(S)-\n'
                '2-bromobutane, to the nearest degree?',
           'a': '23'},
          {'q': 'CHEMISTRY Short Answer: What class of molecules is characterized by the functional group containing '
                'atoms C-O-O-H?',
           'a': 'CARBOXYLIC ACID'},
          {'q': 'CHEMISTRY Short Answer: The reaction of 1 mole of nitrogen gas with 3 moles of hydrogen gas to form '
                'two moles of ammonia has an equilibrium constant of 5 x 10-2 at 700 kelvins. What is the equilibrium '
                'constant of the decomposition reaction of 4 moles of ammonia to form 6 moles of hydrogen gas and 2 '
                'moles of nitrogen gas, at the same temperature and volume?',
           'a': '400'},
          {'q': 'CHEMISTRY Short Answer: What heteroatom is characteristically found in thiols [THIGH- awls], '
                'thioethers, and thioesters?',
           'a': 'SULFUR'},
          {'q': 'CHEMISTRY Short Answer: How many orbitals are in subshells with the azimuthal [ay-zih-MYOO-tul] '
                'quantum number equal to zero?',
           'a': 'ONE'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following is TRUE concerning the hydroxide ion and its '
                'sulfur-containing counterpart, hydrosulfide?\n'
                'W) Hydrosulfide is more polarizable and more basic than hydroxide\n'
                'X) Hydrosulfide is more polarizable and less basic than hydroxide\n'
                'Y) Hydrosulfide is less polarizable and less basic than hydroxide\n'
                'Z) Hydrosulfide is less polarizable and more basic than hydroxide',
           'a': 'X'},
          {'q': 'CHEMISTRY Short Answer: Assume that a 0.1 molar solution of a certain weak acid has a pH of 4.0. To '
                'the nearest integer, what is the pKa of this weak acid?',
           'a': '7'},
          {'q': 'CHEMISTRY Short Answer: How many valence electrons does atomic silicon have?', 'a': 'FOUR'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three quantities that increase when the '
                'electron in a hydrogen atom transitions from 1s to 2s: 1) Energy of the electron; 2) Value of '
                'azimuthal quantum number; 3) Value of principal quantum number.',
           'a': '1 AND 3'},
          {'q': 'CHEMISTRY Short Answer: Order the following three solvents from least to greatest by the pKa of '
                'acetic acid when dissolved in that solvent: 1) DMSO; 2) Water; 3) Methanol.',
           'a': '2, 3, 1'},
          {'q': 'CHEMISTRY Short Answer: Order the following three colors of light from least energetic to most '
                'energetic: 1) Yellow; 2) Violet; 3) Red.',
           'a': '3, 1, 2'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three intermolecular forces that will arise '
                'between molecules of methanol: 1) London forces; 2) Dipole-dipole interactions; 3) Hydrogen bonding.',
           'a': 'ALL OF THEM'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are true regarding carbon '
                'and graphite: 1) Carbon atoms in diamond are sp3 hybridized; 2) Graphite is a better conductor of '
                'electricity than diamond; 3) Graphite carbon is tetrahedral.',
           'a': '1 AND 2'},
          {'q': 'CHEMISTRY Short Answer: Gloria transfers 10 milliliters of an ideal gas at 200,000 kilopascals to a 1 '
                'liter flask. In kilopascals, what is the final pressure of the gas?',
           'a': '2000'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are TRUE concerning '
                'colligative properties: 1) Boiling point elevation is proportional to the molality of particles in a '
                'solution; 2) The Van’t Hoff factor for calcium chloride is close to 2; 3) Adding a solid solute often '
                'increases the vapor pressure of a solution.',
           'a': '1'},
          {'q': 'CHEMISTRY Short Answer: Consider a gaseous mixture of helium and molecular hydrogen that is allowed '
                'to equilibrate to a constant internal temperature. What is the ratio of the root-mean- square speed '
                'of hydrogen molecules to that of helium atoms?',
           'a': 'SQUARE ROOT OF 2'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three organic reactions in which carbon atoms '
                'are reduced: 1) Transformation of alkanes into alcohols; 2) Transformation of ketones into secondary '
                'alcohols; 3) Transformation of carboxylic acids into aldehydes.',
           'a': '2 AND 3'},
          {'q': 'CHEMISTRY Short Answer: Molten cryolite is used in what industrial process?',
           'a': 'HALL-HEROULT PROCESS'},
          {'q': 'CHEMISTRY Short Answer: In VSEPR theory, what is the angle, in degrees, between adjacent bonds in an '
                'octahedral molecule?',
           'a': '90'},
          {'q': 'CHEMISTRY Short Answer: Order the following three ions from smallest to largest in terms of ionic '
                'radii: 1) Cl minus; 2) Br minus; 3) O two minus.',
           'a': '3, 1, 2'},
          {'q': 'CHEMISTRY Short Answer: What is the general term for the type of catalyst one would use when reacting '
                'two immiscible substances or substances in different phases?',
           'a': 'PHASE-TRANSFER CATALYST'},
          {'q': 'CHEMISTRY Short Answer: What is the name for the change in rate of reaction when one of the atoms in '
                'the reactants is substituted with one of its isotopes?',
           'a': 'KINETIC ISOTOPE EFFECT'},
          {'q': 'CHEMISTRY Short Answer: Selenous acid is a weak diprotic acid with formula H SeO . Its\n'
                '2 3 first pKa value is 2.5 and its second is 7.3. To one decimal place, what is the pH of a 1 molar '
                'solution of sodium hydroselenite [high-droh-SELL-en-ite], the amphiprotic [amfih-PRO-tik] salt of '
                'selenous acid?',
           'a': '4.9'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are ALWAYS true regarding '
                'an adiabatic process: 1) Change in internal energy equals zero; 2) Heat transfer equals zero;\n'
                '3) Change in internal energy equals heat transfer.',
           'a': '2'},
          {'q': 'CHEMISTRY Short Answer: In organic synthesis, what metal is added to alkyl halides to generate '
                'nucleophilic [NU-klee-oh-FIL-ik] Grignard [GRIN-yerd] reagents that can react with ketones and '
                'aldehydes?',
           'a': 'MAGNESIUM'},
          {'q': 'CHEMISTRY Short Answer: What is the molecular geometry of SOCl ?\n2', 'a': 'TRIGONAL PYRAMIDAL'},
          {'q': 'CHEMISTRY Short Answer: The lattice enthalpy of a solid cannot be measured directly, but it can be '
                "measured through application of Hess's law to a series of physical and chemical changes. What is the "
                'term for this closed path of steps?',
           'a': 'BORN-HABER CYCLE'},
          {'q': 'CHEMISTRY Short Answer: One of the most important industrial uses of vanadium\n'
                '[vuh-NAY-dee-um] pentoxide is as a catalyst for the production of what acid?',
           'a': 'SULFURIC'},
          {'q': 'CHEMISTRY Short Answer: What is the name for the phenomenon in which electrons move from an atomic '
                'orbital on one atom to the pi-star antibonding orbital of another, when available?',
           'a': 'PI BACKBONDING'},
          {'q': 'CHEMISTRY Short Answer: The ideal gas constant is another form of what other constant, but written in '
                'energy per unit temperature per mole rather than energy per unit temperature per particle?',
           'a': 'BOLTZMANN CONSTANT'},
          {'q': 'CHEMISTRY Short Answer: What is the molecular geometry about the nitrogen atoms in hydrazine '
                '[HIGH-drah-zeen]?',
           'a': 'TRIGONAL PYRAMIDAL'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following statements best explains why triethylamine '
                '[try-ethil-ah-MEEN] is more basic than ammonia?\n'
                'W) Alkyl groups elevate the energy of nitrogen’s nonbonding HOMO\n'
                'X) Alkyl groups lower the energy of nitrogen’s nonbonding HOMO\n'
                'Y) Alkyl groups elevate the energy of nitrogen’s nonbonding LUMO\n'
                'Z) Alkyl groups lower the energy of nitrogen’s nonbonding LUMO',
           'a': 'W'},
          {'q': 'CHEMISTRY Short Answer: The salt lithium fluoride is far less soluble than both lithium iodide and '
                'potassium fluoride. What theory explains this by characterizing Lewis acids and bases in terms of '
                'polarizability and charge density?',
           'a': 'HARD-SOFT ACID BASE'},
          {'q': 'CHEMISTRY Multiple Choice: Which of the following ions is most similar in ionic radius to the cation '
                'Na+?\n'
                'W) K+\n'
                'X) Rb+\n'
                'Y) Mg2+\n'
                'Z) Ca2+',
           'a': 'Z'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three organic acids that would be more acidic '
                'in water than in acetic acid: 1) Chloroacetic acid; 2) Formic acid; 3) Propanoic acid.',
           'a': '1 AND 2'},
          {'q': 'CHEMISTRY Short Answer: The rate of a reaction between reagent A and reagent B is first order in B. '
                'By what factor is the rate of reaction multiplied if the concentration of reagent B is doubled?',
           'a': '2'},
          {'q': 'CHEMISTRY Short Answer: What process, whose first oxidative step is catalyzed in the atmosphere by '
                'dust grains and industrially by vanadium pentoxide, generates oleum, which is reacted with water to '
                'make sulfuric acid?',
           'a': 'CONTACT PROCESS'},
          {'q': 'CHEMISTRY Short Answer: What scientist, whose graduate students Geiger and Marsden performed an '
                'experiment that involved shooting alpha particles at a metallic foil, was the first to propose that '
                'an atom consisted of a dense positively-charged nucleus with mobile electrons surrounding the '
                'nucleus?',
           'a': 'ERNEST RUTHERFORD'},
          {'q': 'CHEMISTRY Short Answer: Identify all of the following three statements that are TRUE concerning '
                'crystal field theory: 1) Carbon monoxide is a strong-field ligand; 2) Tetrahedral splitting is larger '
                'than octahedral splitting; 3) Square planar compounds can be chiral.',
           'a': '1'},
          {'q': 'CHEMISTRY Short Answer: Rank the following three solid structures from the one with the lowest '
                'coordination number to the one with the highest: 1) Body-centered cubic; 2) Hexagonal closest-packed; '
                '3) Simple cubic.',
           'a': '3, 1, 2'},
          {'q': 'CHEMISTRY Short Answer: What rule, which can be explained by the preferential stability of highly '
                'substituted carbocations, predicts that the major product in an elimination reaction with an '
                'unhindered base is the most substituted alkene?',
           'a': "ZAITSEV'S RULE"}],
 'bio': [{'q': 'BIOLOGY Short Answer: The webbed hand of a human embryo develops into five separate fingers by a '
               'process of programmed cell death. What is the term for this process?',
          'a': 'APOPTOSIS'},
         {'q': 'BIOLOGY Multiple Choice: What is the probability of obtaining an F1 purple pea flower if purple is '
               'dominant, white is recessive, and a parental cross is made between a heterozygous purple and '
               'homozygous white flower?\n'
               'W) 1/8\n'
               'X) 1/4\n'
               'Y) 1/2\n'
               'Z) 1',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following best describes how oxygen is stored in the muscles?\n'
               'W) Spread throughout\n'
               'X) Bound to hemoglobin\n'
               'Y) Bound to calmodulin\n'
               'Z) Bound to myoglobin',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following examples is NOT evidence for evolution from a common '
               'ancestor?\n'
               'W) All living things have basic cell processes that are similar and use similar molecules\n'
               'X) Hox genes, or homeotic genes, control vertebrate body plans and are homologous in all vertebrates\n'
               "Y) Even though snakes don't have legs, some snake embryos have limb buds during development similar to "
               'other reptile embryos\n'
               'Z) Bats and birds both have wings that are adaptations for flying',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: As the average temperature dropped during the last glacial period, a species '
               'of cave bears evolved a layer of thicker fur. What kind of selection is this an example of?\n'
               'W) Speciation\n'
               'X) Disruptive selection\n'
               'Y) Stabilizing selection\n'
               'Z) Directional selection',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: What substance composes the frustule [FRUH-stool] of a diatom?\n'
               'W) Silica\n'
               'X) Cellulose\n'
               'Y) Keratin\n'
               'Z) Calcium carbonate',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is NOT true about plant physiology?\n'
               'W) Meristematic [meh-rih-stuh-MAT-ic} tissue located at the tips of stems and roots forms the apical '
               '[A-pik-ul] meristems [MEH-rih-stems]\n'
               'X) Some plants, like shrubs, have lateral meristems\n'
               'Y) Vascular and cork cambium [KAM-bee-um] are produced by apical meristems\n'
               'Z) Intercalary [In-TER-cah-lair-ee] meristems allow grass to grow even after it has been mowed',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: The high sugar content of honey gives it the ability to suppress growth of '
               'nearly all microbes via what kind of pressure on potentially colonizing cells?',
          'a': 'OSMOTIC PRESSURE'},
         {'q': 'BIOLOGY Multiple Choice: The citric acid cycle is a component of what kind of metabolic process?\n'
               'W) Aerobic respiration\n'
               'X) Anaerobic respiration\n'
               'Y) Fermentation\n'
               'Z) Photosynthesis',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following best describes a lysogenic cell?\n'
               'W) It contains a prophage\n'
               'X) It is immune to viral infection\n'
               'Y) It is actively producing viral particles\n'
               'Z) It is about to lyse',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following processes is used to produce additional\n'
               'ATP for the light-independent reactions of photosynthesis?\n'
               'W) Cyclic electron flow\n'
               'X) Lactic acid fermentation\n'
               'Y) Glycolysis [glye-KAWL-eh-sis]\n'
               'Z) Beta oxidation',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: Place the following four structures in order from inside to outside for stems '
               'with a vascular cylinder: 1) Pericycle; 2) Cortex; 3) Epidermis; 4) Pith.',
          'a': '4, 1, 2, 3'},
         {'q': 'BIOLOGY Multiple Choice: Membrane depolarization of an action potential is able to pass from one '
               'cardiac cell to another through what type of connection between cells?\n'
               'W) Desmosomes\n'
               'X) Tight junction\n'
               'Y) Occluding junction\n'
               'Z) Gap junction',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following statements best describes the difference in responses '
               'of plasma cells and cytotoxic T-cells?\n'
               'W) Plasma cells respond the first time the invader is present, cytotoxic T-cells respond subsequent '
               'times\n'
               'X) Plasma cells execute the cell-mediated response, cytotoxic T-cells execute the humoral response\n'
               'Y) Plasma cells secrete antibodies against a pathogen, cytotoxic T-cells kill virus-infected cells\n'
               'Z) Plasma cells confer active immunity, cytotoxic T-cells confer passive immunity',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three statements that are true regarding '
               'lysosomes: 1) Lysosomal enzymes are active at acidic pH; 2) Lysosomes are implicated in inclusion-cell '
               'disease; 3) Lysosomes are formed from late endosomes.',
          'a': '1, 2 AND 3'},
         {'q': "BIOLOGY Short Answer: The term capnophile, used to describe a microbe, refers to the microbe's "
               'preference for environments high in what?',
          'a': 'CARBON DIOXIDE'},
         {'q': 'BIOLOGY Short Answer: How many chromosomes does a human gamete contain?', 'a': '23'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following describes the relationship between glucose and '
               'fructose?\n'
               'W) Structural isomers\n'
               'X) Diastereomers [dye-ah-STARE-ee-oh-mers]\n'
               'Y) Epimers\n'
               'Z) Enantiomers [en-AN-tee-oh-mirz]',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following electrophoresis methods is used to analyze\n'
               'RNA?\n'
               'W) Northern Blot\n'
               'X) Southern Blot\n'
               'Y) Eastern Blot\n'
               'Z) Western Blot',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: All of the following changes would result in an increase in blood pressure, '
               'except:\n'
               'W) Increased cardiac output\n'
               'X) Increased heart rate\n'
               'Y) Increased diameter of arterioles\n'
               'Z) Increased stroke volume',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Topoisomerases [toh-poh-eye-SAW-mer-aces] are involved in which of the '
               'following processes?\n'
               'W) DNA transcription\n'
               'X) DNA replication\n'
               'Y) RNA translation\n'
               'Z) RNA processing',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: What early developmental stage of an animal follows the morula stage and '
               'consists of a single, spherical layer of cells enclosing a hollow, central cavity?',
          'a': 'BLASTULA'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following hormones is a precursor of both estrogen and '
               'testosterone?\n'
               'W) Cortisol\n'
               'X) Ergosterol [ur-GAWS-tur-awl]\n'
               'Y) Aldosterone [al-DOSS-ter-own]\n'
               'Z) DHEA',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Based on the formation of a phragmoplast [FRAG-moh-plast], which of the '
               'following pairs of organisms are most closely related?\n'
               'W) Cyanobacteria and ameobas\n'
               'X) Land plants and green algae\n'
               'Y) Red algae and brown algae\n'
               'Z) Land plants and cyanobacteria',
          'a': 'X'},
         {'q': 'BIOLOGY Multiple Choice: In what organ are dietary fats primarily absorbed?\n'
               'W) Small intestine\n'
               'X) Large intestine\n'
               'Y) Stomach\n'
               'Z) Liver',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Sepals, petals, and which of the following provide the most complete '
               'description for the floral parts that could be found in a single flower of a monoecious plant '
               'species?\n'
               'W) Stamens and carpels\n'
               'X) Filaments\n'
               'Y) Carpels\n'
               'Z) Pistils',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following structures is referred to as our body’s internal '
               'gyroscope?\n'
               'W) Inner ears\n'
               'X) Eyes\n'
               'Y) Outer ears\n'
               'Z) Nose',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Heartwood and sapwood consist of which of the following?\n'
               'W) Bark\n'
               'X) Secondary xylem\n'
               'Y) Periderm\n'
               'Z) Secondary phloem',
          'a': 'X'},
         {'q': 'BIOLOGY Multiple Choice: What material typically constitutes the cell wall in fungi?\n'
               'W) Cellulose\n'
               'X) Peptidoglycan\n'
               'Y) Pectin\n'
               'Z) Chitin',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is NOT an example of a stone fruit?\n'
               'W) Almond\n'
               'X) Coconut\n'
               'Y) Cherry\n'
               'Z) Apple',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following describes antibody-dependent cell- mediated '
               'cytotoxicity?\n'
               'W) An invertebrate host defense mechanism\n'
               'X) Achieved via the classical complement pathway\n'
               'Y) Mediated by Fc receptors on NK cells and myeloid leukocytes\n'
               'Z) The primary cytotoxic pathway mediated by T cells',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is NOT a biogenic amine?\n'
               'W) Dynorphin [dye-NOR-fin]\n'
               'X) Norepinephrine [NOR-eh-pih-NEH-frin]\n'
               'Y) Dopamine\n'
               'Z) Histamine',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Maple syrup is extracted from maple trees by tapping what part of the plant?\n'
               'W) Xylem [ZYE-lum]\n'
               'X) Phloem [FLOW-em]\n'
               'Y) Cambium [KAM-bee-um]\n'
               'Z) Bark',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following types of cells could one find surrounding a stomatal '
               'pore?\n'
               'W) Guard cells\n'
               'X) Mesophyll [MEH-zoh-fill] cells\n'
               'Y) Palisade cells\n'
               'Z) Trace cells',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following vitamins is NOT synthesized by plants or animals?\n'
               'W) B12\n'
               'X) B6\n'
               'Y) B2\n'
               'Z) C',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is thought to have been the beneficial effect of two '
               'entire genome duplication events in the vertebrate lineage?\n'
               'W) More copies of each gene per cell were insurance against DNA damage from increased solar radiation\n'
               'X) Polyploid animals were more likely to have one good copy of each gene\n'
               'Y) One copy of a duplicated gene was free to take on new functions\n'
               'Z) Four copies of each gene meant stronger gene responses',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: What form of active transport involves moving two or more different molecules '
               'across a membrane in the same direction, coupling the favorable transport of one molecule to the '
               'unfavorable transport of the other?',
          'a': 'SYMPORT'},
         {'q': 'BIOLOGY Multiple Choice: Mycobacterium [MY-koh-bacterium] is a genus of slow-growing and '
               'difficult-to-eradicate bacteria responsible for what two human diseases?\n'
               'W) Mononucleosis and pertussis [per-TUH-sis]\n'
               'X) Shigella [shih-GEHL-ah]and malaria\n'
               'Y) Gingivitis and impetigo [im-puh-tie-goh]\n'
               'Z) Leprosy and tuberculosis',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Bacteria are able to become resistant to antibiotics by increasing their '
               'genetic variability through all of the following mechanisms EXCEPT:\n'
               'W) Conjugation\n'
               'X) Transduction\n'
               'Y) Binary fission\n'
               'Z) Transformation',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: In humans, the mucosa of the stomach produces intrinsic factor, which is '
               'required for absorption of what vitamin?',
          'a': 'B12'},
         {'q': 'BIOLOGY Multiple Choice: One species resembles another species that is poisonous. What is this '
               'phenomenon called?\n'
               'W) Commensalism [kah-MEN-sul-ism]\n'
               'X) Mutualism\n'
               'Y) Batesian mimicry [BAIT-see-in MIM-ih-kree]\n'
               'Z) Mullerian mimicry [muhl-AIR-ee-an MIM-ih-kree]',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: What human organ utilizes the most glucose in the body?\n'
               'W) Liver\n'
               'X) Heart\n'
               'Y) Lungs\n'
               'Z) Brain',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Plant cells are distinguished from animal cells by having:\n'
               'W) A large central vacuole, chloroplasts, and a cell wall made of cellulose\n'
               'X) A large central vacuole, mitochondria, and a nucleus\n'
               'Y) A cell wall made of cellulose, Golgi apparatus, and chloroplasts\n'
               'Z) Chloroplasts, mitochondria, and a nucleus',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following plant hormones plays the largest role in the '
               'germination of a seed?\n'
               'W) Cytokinin [sye-toh-KYE-nin]\n'
               'X) Zeatin [ZEE-ah-tin]\n'
               'Y) Gibberellins [jib-er-ELL-ins]\n'
               'Z) Ethylene',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: Liverworts are a part of which nonvascular plant phylum?',
          'a': 'MARCHANTIOPHYTA'},
         {'q': 'BIOLOGY Short Answer: Tetanus is a disease caused by what genus of endospore-forming bacteria?',
          'a': 'CLOSTRIDIUM'},
         {'q': 'BIOLOGY Multiple Choice: If the only method of introducing genetic variation into a sample population '
               'of E. coli is by spontaneous mutation, which of the following is the best way to increase the '
               'prevalence of beneficial mutations over many generations?\n'
               'W) Conjugation\n'
               'X) Binary fission\n'
               'Y) Transduction\n'
               'Z) Horizontal gene transfer',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: What is the name for skeletal muscle cells containing multiple nuclei?',
          'a': 'SYNCYTIUM'},
         {'q': 'BIOLOGY Multiple Choice: A plant has a somatic chromosome number of 2n = 22. After a cell in this '
               'plant undergoes mitosis, how many chromosomes will the daughter cells each have?\n'
               'W) 11\n'
               'X) 22\n'
               'Y) 33\n'
               'Z) 44',
          'a': 'X'},
         {'q': 'BIOLOGY Multiple Choice: SDS is a detergent. Which of the following explains how SDS denatures '
               'proteins?\n'
               'W) Interferes with the hydrophobic interactions that normally stabilize the proteins\n'
               'X) Interferes with the hydrophillic interactions that normally stabilize the proteins\n'
               'Y) Interferes with the amphiphillic [amfih-FILL-ic] interactions that normally stabilize the proteins\n'
               'Z) Breaks the peptide bonds',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: The water-proof layer within the endodermis of the root that filters '
               'substances entering a plant is called the:\n'
               'W) Pericycle\n'
               'X) Hypodermis\n'
               'Y) Casparian strip\n'
               'Z) Vascular cambium',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: What terrestrial biome occurs in mid-latitude coastal regions and is found in '
               'Mediterranean climates such as California?',
          'a': 'CHAPARRAL'},
         {'q': 'BIOLOGY Short Answer: In female mammalian cells, the second X chromosome is generally silenced. What '
               'term is used to describe the condensed inactive X chromosome?',
          'a': 'BARR BODY'},
         {'q': 'BIOLOGY Multiple Choice: If you needed to find a sample of simple cuboidal epithelium [eh- '
               'pih-THEEL-ee-um] in the human body, you would want tissue from which of the following organs?\n'
               'W) Kidneys\n'
               'X) Lungs\n'
               'Y) Esophagus\n'
               'Z) Stomach',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: In regard to human anatomy, with which of the following is\n'
               'Wolff’s law concerned?\n'
               'W) The shape of bone being determined by mechanical and gravitational stresses\n'
               'X) The negative feedback loops that control production of thyroid hormone\n'
               'Y) The forces generated by isotonic contractions of skeletal muscle\n'
               'Z) The electrical potential of resting cardiac cells',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: What name is used to describe the ability of a microbe to respond to changes in '
               'local microbial population density?',
          'a': 'QUORUM SENSING'},
         {'q': 'BIOLOGY Short Answer: What term best describes a plant that has parallel leaf veins, fibrous roots, '
               'and flowers with parts in threes?',
          'a': 'MONOCOT'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following human cell types do NOT perform aerobic respiration?\n'
               'W) Red blood cells\n'
               'X) Heart muscle cells\n'
               'Y) Hair cells\n'
               'Z) Outer skin cells',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: What plant hormone mediates phototropism?', 'a': 'AUXIN'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is NOT a location where bile is either stored or '
               'travels to after it is made?\n'
               'W) Gall bladder\n'
               'X) Cystic duct\n'
               'Y) Pancreatic duct\n'
               'Z) Duodenum',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: Ced-3 and ced-4 are genes likely involved in what cell process?',
          'a': 'APOPTOSIS'},
         {'q': 'BIOLOGY Multiple Choice: In the human skull, which of the following bones does NOT contain a sinus?\n'
               'W) Frontal\n'
               'X) Sphenoid [SFEE-noyd]\n'
               'Y) Maxillae [MAX-il-eye]\n'
               'Z) Lacrimal',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following receptors could NOT be found on the surface of a '
               'cell?\n'
               'W) Laminar receptor\n'
               'X) Ion-channel coupled receptor\n'
               'Y) Tyrosine [TIE-row-seen] kinase receptor\n'
               'Z) G-protein coupled receptor',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: What system, widely dispersed in eukaryotes, is sometimes used for a similar '
               'immune function as the CRISPR[crisper]/Cas9 system, and also used for endogenous gene regulation?',
          'a': 'RNAI'},
         {'q': 'BIOLOGY Short Answer: Trans fats are produced from unsaturated fats in what chemical process?',
          'a': 'HYDROGENATION'},
         {'q': 'BIOLOGY Short Answer: 5-methylcytosine [methil-SYE-toh-seen] is particularly susceptible to mutations '
               'because upon deamination [dee-am-ih-NAY-shun], it becomes what other nucleobase?',
          'a': 'THYMINE'},
         {'q': 'BIOLOGY Short Answer: A scientist has pea plants that are homozygous for purple flowers and plants '
               'that are homozygous for white flowers. Given that the purple flower trait is dominant, if the plants '
               'are crossed and then the resulting F1 generation is allowed to self-pollinate, what percentage of the '
               'resulting F2 plants will have white flowers?',
          'a': '25'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following molecules is most similar in structure to vitamin A?\n'
               'W) Beta carotene\n'
               'X) Tocopherol [toh-KOF-ur-all]\n'
               'Y) Dopamine\n'
               'Z) Estradiol [es-trah-DYE-awl]',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: The suprachiasmatic nucleus is involved in controlling which of the '
               'following?\n'
               'W) Circadian rhythms\n'
               'X) Body temperature\n'
               'Y) Heart rate\n'
               'Z) Respiration rate',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following disorders is due to a dominant trait?\n'
               'W) Cystic fibrosis\n'
               'X) Hemophilia [HEE-moh-FEEL-ee-ah]\n'
               'Y) Albinism [AL-bah-nih-zim]\n'
               'Z) Polydactyly [polly-DAK-til-ee]',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following types of microscopy require the specimen to be '
               'subjected to a vacuum?\n'
               'W) Fluorescence\n'
               'X) Transmission electron\n'
               'Y) Scanning tunneling\n'
               'Z) Dark field',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: What type of learning involves an animal associating a behavioral response with '
               'punishment or reward?',
          'a': 'OPERANT LEARNING'},
         {'q': 'BIOLOGY Multiple Choice: Most cells are exposed to extracellular glucose concentrations higher than '
               'those inside the cell. Glucose is taken up by these cells via which of the following?\n'
               'W) Osmosis\n'
               'X) Active transport\n'
               'Y) Exocytosis\n'
               'Z) Facilitated diffusion',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following mutations would most likely result in a frame-shift '
               'mutation?\n'
               'W) Single base substitution\n'
               'X) Triple base substitution\n'
               'Y) Single base deletion\n'
               'Z) Triple base deletion',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: The size of most mammalian cells is closest to which of the following?\n'
               'W) 1 picometer\n'
               'X) 1 micrometer\n'
               'Y) 1 millimeter\n'
               'Z) 1 centimeter',
          'a': 'X'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following proteins is involved with prokaryotic transcription?\n'
               'W) DNA polymerase [paw-LIM-er-ace] 3\n'
               'X) Sigma factor\n'
               'Y) Elongation factor\n'
               'Z) Amino acyl tRNA synthetase [ahMEEno-ASS-il tee-R.N.A. SIN-thah-tase]',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: The selective loss of dopaminergic [dope-ah-min-UR-jik] neurons in the '
               'substantia nigra [NYE-grah] is characteristic of what neurodegenerative disease?',
          'a': 'PARKINSON’S DISEASE'},
         {'q': 'BIOLOGY Short Answer: Chondrocytes are associated with what structural material found in joints and '
               'spinal disks?',
          'a': 'CARTILAGE'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three macromolecules that are digested primarily '
               'in the stomach: 1) Starches; 2) Nucleic acids; 3) Proteins.',
          'a': '3'},
         {'q': 'BIOLOGY Short Answer: The white matter in the spinal cord appears white because the neurons are '
               'covered with what substance?',
          'a': 'MYELIN'},
         {'q': 'BIOLOGY Short Answer: During DNA replication, what protein is responsible for negatively supercoiling '
               'the DNA to relieve strain?',
          'a': 'TOPOISOMERASE'},
         {'q': 'BIOLOGY Short Answer: What type of muscle contraction is NOT associated with a change in length?',
          'a': 'ISOMETRIC'},
         {'q': 'BIOLOGY Short Answer: Tandem mass spectrometry is a technique that can be used to determine the '
               'primary structure of a protein. What two amino acids can mass spectrometry NOT differentiate?',
          'a': 'ISOLEUCINE AND LEUCINE'},
         {'q': 'BIOLOGY Short Answer: A glutamate to valine mutation is well-known to be responsible for what disease '
               'that is associated with resistance to malaria?',
          'a': 'SICKLE CELL ANEMIA'},
         {'q': 'BIOLOGY Multiple Choice: Your teacher has a passion for studying human immunoglobulins, but they have '
               'to be dimers. What immunoglobulin does your teacher study?\n'
               'W) IgD\n'
               'X) IgA\n'
               'Y) IgM\n'
               'Z) IgE',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: The products of the reaction catalyzed by pancreatic lipase are fatty acids and '
               'what other molecule?',
          'a': 'GLYCEROL'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three structures that can be found in both '
               'bacteria and plants: 1) Nucleus; 2) Peroxisome [per-OX-ih-sowm]; 3) Mitochondrion.',
          'a': 'NONE OF THEM'},
         {'q': 'BIOLOGY Short Answer: What vitamin, essential to humans, is involved in collagen synthesis?',
          'a': 'VITAMIN C'},
         {'q': 'BIOLOGY Short Answer: Order the following three parts of the digestive tract from first to last to be '
               'encountered by a bolus: 1) Ileum [ILL-ee-um]; 2) Transverse colon; 3) Pyloric sphincter[SFEENK-ter].',
          'a': '3, 1, 2'},
         {'q': 'BIOLOGY Short Answer: What amino acid possesses a secondary amine functionality and as a result, has '
               'special constraints on its secondary structure?',
          'a': 'PROLINE'},
         {'q': 'BIOLOGY Multiple Choice: p53 is a protein associated with which of the following processes?\n'
               'W) Cell cycle\n'
               'X) Transciption\n'
               'Y) Electron transport chain\n'
               'Z) Heme synthesis',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: What hormone, secreted by the posterior pituitary, plays a role in water '
               'retention in the kidneys?',
          'a': 'VASOPRESSIN'},
         {'q': 'BIOLOGY Short Answer: What group of biotech-relevant enzymes, derived from bacteria, often recognize '
               'specific palindromic sequences of nucleic acids and introduce a double-stranded break?',
          'a': 'RESTRICTION ENZYMES'},
         {'q': 'BIOLOGY Multiple Choice: An effective enzyme has a very high affinity for which of the following?\n'
               'W) Starting materials\n'
               'X) Products\n'
               'Y) Transition state\n'
               'Z) ATP',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: What enzyme, found in the human stomach, is activated by hydrochloric acid and '
               'breaks down proteins?',
          'a': 'PEPSIN'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three pathways during which oxidative '
               'phosphorylation [faws-four-il-AY-shun] occurs: 1) Photosynthesis; 2) Krebs cycle; 3) Electron '
               'transport chain.',
          'a': '1 AND 3'},
         {'q': 'BIOLOGY Short Answer: In the presence of high amounts of citrate, the reaction catalyzed by the '
               'glycolytic enzyme phosphofructokinase [faws-fo-frook-tow-KYE-nase] slows down. Identify all of the '
               'following three types of enzyme inhibition that occur in this example: 1) Competitive; 2)\n'
               'Allosteric; 3) Feedback.',
          'a': '2 AND 3'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is NOT considered to be a tumor suppressor protein?\n'
               'W) Rb\n'
               'X) PTEN\n'
               'Y) HER2/neu [her-TWO - new]\n'
               'Z) p53',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: To prevent the body from metabolizing Drug G too quickly, a pharmaceutical '
               'company develops Substance Q to be taken concurrently with Drug G. If Substance\n'
               'Q binds to the enzyme catalyzing the metabolism of Drug G and alters its active site, what type of '
               'inhibition is occuring?',
          'a': 'NON-COMPETITIVE INHIBITION'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following four plant structures that are determinate:\n'
               '1) Leaves; 2) Shoot apical meristems; 3) Root apical meristems; 4) Flowers.',
          'a': '1, 4'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following provides the best example of a situation in which '
               'genetic drift would play a significant role within a population?\n'
               'W) Non-random mating among plants with purple flowers leads to inbreeding and homozygous lethal '
               'conditions that prevent seed germination\n'
               'X) In a large population of plants with purple flowers, one individual exhibits white flowers caused '
               'by a mutation\n'
               'Y) In a small population of plants with purple flowers, three white-flowered individuals exist. A deer '
               'eats two of the three white flowered plants, thus removing them from the population\n'
               'Z) In a small population of plants where some individuals have white and some have purple flowers, '
               'bees strongly prefer the purple flowers, thus more seeds are produced from the purple individuals.',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: Phosphofructokinase [faws-fo-frook-tow-KYE-nase] catalyzes the formation of what '
               'molecule from fructose-6-phosphate?',
          'a': 'FRUCTOSE-1,6-BISPHOSPHATE'},
         {'q': 'BIOLOGY Short Answer: Chlorophyll is a pigment that chelates what metal center?', 'a': 'MAGNESIUM'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following hormones is most pronouncedly elevated in a woman '
               'undergoing menopause?\n'
               'W) Follicle-stimulating hormone\n'
               'X) Estrogen\n'
               'Y) Progesterone\n'
               'Z) Testosterone',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: What plant-signaling molecule, similar in structure to aspirin, is thought to be '
               'produced around infection sites and carried by the phloem throughout the plant?',
          'a': 'METHYLSALICYLIC ACID'},
         {'q': 'BIOLOGY Multiple Choice: The phase of the Plasmodium life cycle in which it lives in the salivary '
               'gland of the mosquito is called which of the following?\n'
               'W) Sporozoite [spoor-oh-ZOH-i te]\n'
               'X) Trophozoite [troh-foh-ZOH-i te]\n'
               'Y) Schizont [SKIZ-awnt]\n'
               'Z) Gametocyte',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following four cellular attachments that can be found in '
               'animal cells: 1) Tight junction; 2) Desmosome; 3) Plasmodesmata [plazz-moh-dez-\n'
               'MAH-tah]; 4) Adherens junction.',
          'a': '1, 2, AND 4'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three statements that are TRUE regarding E. coli: '
               '1) Gram negative; 2) Forms spores; 3) Rod-shaped.',
          'a': '1 AND 3'},
         {'q': 'BIOLOGY Short Answer: Dynein [DYE-nee-in] and kinesin [kin-EE-sin] are proteins that bind to what '
               'cytoskeletal features?',
          'a': 'MICROTUBULES'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following amino acids is encoded by a single codon?\n'
               'W) Leucine [LOO-seen]\n'
               'X) Glycine [GLYE-seen]\n'
               'Y) Methionine [meth-IOH-neen]\n'
               'Z) Phenylalanine [Fennel-AL-ahneen]',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following reactions does NOT require biotin?\n'
               'W) Conversion of pyruvate to oxaloacetate [ox-aa-loh-ASS-ah-tate]\n'
               'X) Conversion of acetyl-CoA to malonyl [MAL-uh-nihl]-CoA\n'
               'Y) Conversion of propionyl [PRO-pee-on-il]-CoA to methylmalonyl[meh-thil-MAL-uh-nil]-\n'
               'Z) Conversion of oxaloacetate [ox-aa-loh-ASS-ah-tate] to succinate',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Through what anatomical feature does water exit a sponge?\n'
               'W) Osculum\n'
               'X) Ostium\n'
               'Y) Atrium\n'
               'Z) Coelom [SEE-lum]',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: What is the term for malignant tumors of the connective tissues?',
          'a': 'SARCOMAS'},
         {'q': 'BIOLOGY Multiple Choice: The mechanisms involved in aligning homologous chromosomes in meiosis are '
               'also useful for which of the following?\n'
               'W) Repairing nicks\n'
               'X) Repairing single-stranded breaks\n'
               'Y) Repairing double-stranded breaks\n'
               'Z) Repairing point mutations',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: Cytochrome proteins contain prosthetic groups that possess what metal center?',
          'a': 'IRON'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following correctly describes the difference between peptoids, '
               'or poly-N-substituted glycines, and proteins?\n'
               'W) Peptoids have less constrained secondary structure than proteins\n'
               'X) Peptoids cannot possess tertiary structure, while proteins can\n'
               'Y) Peptoids form more stable alpha helices than proteins\n'
               'Z) Peptoids form more stable beta sheets than proteins',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following lengths of DNA would be least likely to be unwound by '
               'a passive helicase?\n'
               'W) ATATAT\n'
               'X) AAATTT\n'
               'Y) TTTGGG\n'
               'Z) GCGCGC',
          'a': 'Z'},
         {'q': 'BIOLOGY Short Answer: Bacteria use what cellular structure for motility?', 'a': 'FLAGELLUM'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three conditions that negatively impact short term '
               'memory: 1) Post traumatic stress disorder; 2) Aphasia [ah-FAY-sjah]; 3)\n'
               "Alzheimer's.",
          'a': '1, 2, 3'},
         {'q': 'BIOLOGY Short Answer: What organelle is defective in inclusion-cell disease, also known as I-cell '
               'disease?',
          'a': 'LYSOSOME'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following nucleobases is NOT a pyrimidine\n'
               '[pur-RIM-ih-deen]?\n'
               'W) Guanine [GWAH-neen]\n'
               'X) Cytosine [SYE-toh-seen]\n'
               'Y) Thymine [THIGH-meen]\n'
               'Z) Uracil [YUR-ah-sil]',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following immune cells is most involved in defense against '
               'parasites?\n'
               'W) Neutrophils\n'
               'X) Eosinophils [ee-oh-SIN-oh-filz]\n'
               'Y) Basophils [BAY-zoh-filz]\n'
               'Z) Mast cells',
          'a': 'X'}, {'q': 'BIOLOGY Multiple Choice: What is the most abundant protein in the world?\n'
               'W) Hemoglobin\n'
               'X) Rubisco\n'
               'Y) Collagen\n'
               'Z) Actin',
          'a': 'X'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is a constituent of blood plasma but NOT of blood '
               'serum?\n'
               'W) Hemoglobin\n'
               'X) Fibrinogen [fye-BRIN-oh-jen]\n'
               'Y) Albumin [al-BYOO-min]\n'
               'Z) Urea',
          'a': 'X'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following statements is true of root hairs?\n'
               'W) They increase the surface area of the root for absorption of water\n'
               'X) They are located in each stomate on the root\n'
               'Y) They are found on both stems and roots\n'
               'Z) They are involved in mechanical stabilization of the plant',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: To what phylum [FYE-lum] do snails belong?', 'a': 'MOLLUSCA'},
         {'q': 'BIOLOGY Short Answer: What human organ produces fibrinogen [fye-BRIN-oh-jen]?', 'a': 'LIVER'},
         {'q': 'BIOLOGY Multiple Choice: In humans, the suprachiasmatic nucleus or "biological clock" is located in '
               'which of the following parts of the brain?\n'
               'W) Pineal [PIN-ee-ul] gland\n'
               'X) Hypothalamus [high-poh-THAL-ah-mus]\n'
               'Y) Cerebral [seh-REE-brul] cortex\n'
               'Z) Cerebellum [sarah-BELL-um]',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: In what human organ can one find cells possessing intercalated '
               '[in-TER-cah-lated] disks?',
          'a': 'HEART'},
         {'q': 'BIOLOGY Short Answer: In protostomes, what structure does the blastopore become?', 'a': 'MOUTH'},
         {'q': 'BIOLOGY Multiple Choice: The three-dimensional or folded shape of a protein is what hierarchical '
               'structure level?\n'
               'W) Primary\n'
               'X) Secondary\n'
               'Y) Tertiary\n'
               'Z) Quaternary',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is NOT a basis for assays to measure cell numbers or '
               'cell proliferation?\n'
               'W) Presence of cell proliferation antigens\n'
               'X) Rate of DNA replication\n'
               'Y) Rate of RNA replication\n'
               'Z) Measurement of ATP concentration',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: In what part of a plant is the casparian strip located?\n'
               'W) The bark\n'
               'X) The stomatal guard cells\n'
               'Y) The endodermis of the root\n'
               'Z) The stem cortex',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: What type of symmetry do platyhelminths [plat-ih-HELL-minths] possess?',
          'a': 'BILATERAL'},
         {'q': 'BIOLOGY Short Answer: What type of muscle is found in the intestinal wall?', 'a': 'SMOOTH'},
         {'q': 'BIOLOGY Multiple Choice: Metallothionein [meh-talloh-THIGH-uh-nin] is a protein that has been '
               'engineered into rice in order to promote iron uptake in the small intestine. This is because iron '
               'uptake requires which of the following elements?\n'
               'W) Phosphorus\n'
               'X) Selenium\n'
               'Y) Sulfur\n'
               'Z) Chlorine',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: What type of cells are found in the lacunae [lah-KOO-nay] of cartilage?',
          'a': 'CHONDROCYTES'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three cell types that are leukocytes '
               '[LOO-koh-sites]:\n'
               '1) Eosinophil [ee-oh-SIN-oh-fil]; 2) Basophil [BAY-zoh-fil]; 3) Erythrocyte [eh-RITH-roh-site].',
          'a': '1 AND 2'},
         {'q': 'BIOLOGY Multiple Choice: A deficiency of what trace element can result in goiter?\n'
               'W) Sodium\n'
               'X) Chlorine\n'
               'Y) Potassium\n'
               'Z) Iodine',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is NOT a symptom or sign of a person suffering from '
               'diabetes mellitus ?\n'
               'W) Increase in protein breakdown\n'
               'X) Presence of sugar in urine\n'
               'Y) Decrease in the amount of urine production\n'
               'Z) Increased levels of blood glucose',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is the adjective for a leaf arrangement in which two '
               'leaves are present at each node?\n'
               'W) Opposite\n'
               'X) Alternate\n'
               'Y) Whorled\n'
               'Z) Sessile',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: What is the highest level of protein structure found in hemoglobin?',
          'a': 'QUATERNARY'},
         {'q': 'BIOLOGY Short Answer: What is the name of the muscle attachment point that remains relatively '
               'stationary during contraction?',
          'a': 'ORIGIN'},
         {'q': 'BIOLOGY Multiple Choice: When viewed under a microscope, a eukaryotic [YOU-care-ee-AW-tic] cell has '
               'visible chromosomes. In what phase of the cell cycle is the cell?\n'
               'W) M\n'
               'X) S\n'
               'Y) G1 [G one]\n'
               'Z) G-zero [g-zero]',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: The hamstrings allow flexion of what joint?', 'a': 'KNEE'},
         {'q': 'BIOLOGY Short Answer: In humans, what group of muscles produce extension of the knee joint, such as '
               'during jumping?',
          'a': 'QUADRICEPS'},
         {'q': 'BIOLOGY Multiple Choice: Which chamber in the heart has the highest systolic pressure?\n'
               'W) Right atrium\n'
               'X) Right ventricle\n'
               'Y) Left atrium\n'
               'Z) Left ventricle',
          'a': 'Z'},
         {'q': 'BIOLOGY Short Answer: List the correct order of a secretory protein pathway from synthesis to '
               'secretion:\n'
               '1) Golgi apparatus; 2) Endoplasmic reticulum [reh-TIK-yoo-lum]; 3) Plasma membrane.',
          'a': '2, 1, 3'},
         {'q': 'BIOLOGY Multiple Choice: Grasses provide an example of a root system that is best described as which '
               'of the following?\n'
               'W) Monocot tap\n'
               'X) Dicot tap\n'
               'Y) Monocot fibrous\n'
               'Z) Dicot fibrous',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: If a Gram stain were performed on E. coli [ee COLE-eye] with saffranin '
               '[SAFF-rah-nin] as the counterstain, what color would the bacteria appear to be?',
          'a': 'RED'},
         {'q': 'BIOLOGY Short Answer: What is the repeating unit found in skeletal muscles?', 'a': 'SARCOMERE'},
         {'q': 'BIOLOGY Multiple Choice: Chaperonins [shap-ur-OH-ninz] are involved in which of the following '
               'processes?\n'
               'W) Guiding metabolites to cellular compartments\n'
               'X) Ensuring proper protein folding\n'
               'Y) Breaking down ubiquitin [you-BIH-kwih-tin] tagged proteins\n'
               'Z) Breaking down disaccharides',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: In the sarcomere, what protein is found as filaments twisted into a double '
               'helix?',
          'a': 'ACTIN'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three types of muscle that can contract strongly '
               'even when stretched : 1) Cardiac; 2) Skeletal; 3) Smooth.',
          'a': '3'},
         {'q': 'BIOLOGY Multiple Choice: Sap that is used in making maple syrup is transported by what organ?\n'
               'W) Epidermis\n'
               'X) Xylem\n'
               'Y) Phloem\n'
               'Z) Pith',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: The sliding filament theory of muscle contraction primarily involves what two '
               'proteins?',
          'a': 'ACTIN AND MYOSIN'},
         {'q': 'BIOLOGY Multiple Choice: Apical dominance in plants means that:\n'
               'W) The apical bud stimulates vertical growth\n'
               'X) The apical bud inhibits auxin production\n'
               'Y) The apical bud stimulates floral development\n'
               'Z) The apical bud inhibits the growth of lateral buds',
          'a': 'Z'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three structures that possess a double membrane: '
               '1) Lysosome\n'
               '[LYE-soh-sohm]; 2) Nucleus; 3) Ribosome [RYE-beh-sohme].',
          'a': '2'},
         {'q': 'BIOLOGY Short Answer: Calcium ions activate muscle contraction because they move what protein from '
               'thin filaments?',
          'a': 'TROPOMYOSIN'},
         {'q': 'BIOLOGY Multiple Choice: Ferredoxin is an electron-transfer protein that contains which of the '
               'following?\n'
               'W) Heme [heem] group\n'
               'X) Iron-sulfur cluster\n'
               'Y) Zinc finger\n'
               'Z) Leucine [LOO-seen] zipper',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: What two blood-sugar-relevant hormones are secreted by the islets [EYE-lets] of '
               'Langerhans [LAYN-gur-honz]?',
          'a': 'GLUCAGON AND INSULIN'},
         {'q': 'BIOLOGY Short Answer: What acid is produced by parietal [pah-RYE-eht-ul] cells?',
          'a': 'HYDROCHLORIC ACID'},
         {'q': 'BIOLOGY Multiple Choice: In green plants, energy is stored mainly in which of the following forms?\n'
               'W) Cellulose\n'
               'X) Starch\n'
               'Y) Glucose\n'
               'Z) ATP',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: What sheet of muscle separates the thoracic and abdominopelvic cavities?',
          'a': 'DIAPHRAGM'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following types of tissue do monocot roots possess at their '
               'center that dicot roots do not?\n'
               'W) Xylem\n'
               'X) Pith\n'
               'Y) Collenchyma [koh-LEN-kimma]\n'
               'Z) Trichomes',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three processes that are considered active '
               'transport: 1) Uptake of glucose via channels; 2) Sodium-calcium exchange; 3) Mucus secretion.',
          'a': '2 AND 3'},
         {'q': 'BIOLOGY Short Answer: In collies, what neurotransmitter is released by somatic motor neurons to induce '
               'muscle contraction?',
          'a': 'ACETYLCHOLINE'},
         {'q': 'BIOLOGY Multiple Choice: With which of the following is protein binding to a TATA [TAH-tah] box '
               'activity associated?\n'
               'W) DNA replication\n'
               'X) Transcription\n'
               'Y) Translation\n'
               'Z) Elongation',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: Rickets is caused by a deficiency of what vitamin?', 'a': 'VITAMIN D'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three molecules that are exocrine [EX-oh-krin] '
               'products:\n'
               '1) EGF; 2) Amylase; 3) ADH.',
          'a': '2'},
         {'q': 'BIOLOGY Short Answer: What leukocyte [LOO-koh-site] can have up to a five-lobed nucleus and plays a '
               'role in phagocytosis [fag-oh-sye-TOW-sis] of bacteria?',
          'a': 'NEUTROPHIL'},
         {'q': 'BIOLOGY Short Answer: What type of immune cells use perforins [PUR-fur-ins] to induce cell death in '
               'infected body cells?',
          'a': 'NK CELLS'},
         {'q': 'BIOLOGY Multiple Choice: Sutures are an example of what type of joint?\n'
               'W) Synovial [sin-OH-vee-ul]\n'
               'X) Saddle\n'
               'Y) Disk\n'
               'Z) Immovable',
          'a': 'Z'},
         {'q': "BIOLOGY Multiple Choice: Hansen's disease is caused by which of the following genera of bacteria?\n"
               'W) Streptococcus [strep-toh-kokkus]\n'
               'X) Helicobacter [HEEL-ik-oh-bak-tur]\n'
               'Y) Mycobacterium [MY-koh-bacterium]\n'
               'Z) Vibrio [VIH-bree-oh]',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following organelles would likely contain a high concentration '
               'of catalase\n'
               '[CAT-ah-lace]?\n'
               'W) Glyoxysome [glye-OX-ih-sowm]\n'
               'X) Mitochondrion [my-tow-KON-dree-on]\n'
               'Y) Peroxisome [per-OX-ih-zohm]\n'
               'Z) Chloroplast [KLOR-oh-plast]',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following best describes the relationship between glucose and '
               'fructose?\n'
               'W) Diastereomers [dye-ah-STARE-ee-oh-murz]\n'
               'X) Epimers [eh-pih-mur]\n'
               'Y) Stereoisomers [stereo-EYE-soh-murz]\n'
               'Z) Structural isomers [eye-soh-murz]',
          'a': 'Z'},
         {'q': 'BIOLOGY Short Answer: What area of the eye has a high concentration of cones and is so crucial for '
               'sharp vision that raptors have two?',
          'a': 'FOVEA'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following four options that are examples of determinate '
               'growth in plants: 1) Shoots; 2) Roots; 3) Flowers; 4) Leaves.',
          'a': '3 AND 4'},
         {'q': 'BIOLOGY Short Answer: What type of leukocyte [LOO-koh-site] is involved in phagocytosis '
               '[fag-oh-sye-TOW-sis] of antigen-antibody complexes and parasites?',
          'a': 'EOSINOPHIL'},
         {'q': 'BIOLOGY Short Answer: Angiotensin [an-jee-oh-TEN-sin] acts on the adrenal [Ah-DREE-nul] cortex to '
               'promote secretion of what hormone?',
          'a': 'ALDOSTERONE'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following organisms is characterized as a parazoan '
               '[para-ZOH-an]?\n'
               'W) Sponge\n'
               'X) Sea cucumber\n'
               'Y) Jellyfish\n'
               'Z) Tapeworm',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is an example of simple squamous [SKWAY-mus] '
               'epithelium [eh-pih-THEEL-ee-um]?\n'
               'W) Stomach lining\n'
               'X) Intestinal lining\n'
               'Y) Lung lining\n'
               'Z) Skin',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Zinc finger motifs are commonly found in proteins that do which of the '
               'following?\n'
               'W) Hydrolyze [HIGH-droh-lyze] sugars\n'
               'X) Sequester calcium\n'
               'Y) Catalyze polymerization [pawl-ih-mer-eh-ZAY-shun]\n'
               'Z) Bind to DNA',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is a correct classification of spectrin proteins?\n'
               'W) Transmembrane\n'
               'X) Receptor\n'
               'Y) Channel\n'
               'Z) Cytoskeletal [SIGH-toh-skeletal]',
          'a': 'Z'},
         {'q': 'BIOLOGY Short Answer: What is the net ATP gain during glycolysis [glye-KAWL-eh-sis], per molecule of '
               'glucose?',
          'a': 'TWO'},
         {'q': 'BIOLOGY Short Answer: In a young stem, what is the name for the immature tissues that will '
               'specifically develop into xylem and phloem?',
          'a': 'PROCAMBIUM'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following correctly explains why fish cannot breathe outside of '
               'water?\n'
               'W) Air contains less oxygen than water\n'
               'X) Their gas exchange systems are tuned to dissolved oxygen\n'
               'Y) In air, their gills collapse\n'
               'Z) Air provides more structural support to the fish',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three items that are considered rhizopods: 1) '
               'Kelp; 2) Amoeba;\n'
               '3) Euglenid [you-GLEE-nids].',
          'a': 'JUST 2'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following is an example of a Chrysophytan [Cris-AW-fih-tan]?\n'
               'W) Amoeba [ah-MEE-bah]\n'
               'X) Trypanoma [trih-pan-OH-ma]\n'
               'Y) Plasmodium [plazz-MOH-dee-um]\n'
               'Z) Diatom [DYE-ah-tom]',
          'a': 'Z'},
         {'q': 'BIOLOGY Short Answer: Given that hemoglobin is 144 amino acids long, identify all of the following '
               'three numbers of nucleotides that can be in the primary mRNA transcript of hemoglobin at different '
               'stages of processing:\n'
               '1) 144; 2) 432; 3) 1356.',
          'a': 'JUST 3'},
         {'q': 'BIOLOGY Short Answer: What structural molecule do Gram positive bacteria possess in large quantities?',
          'a': 'PEPTIDOGLYCAN'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three types of ion channels that are open during '
               'the falling phase of the action potential: 1) Voltage gated sodium; 2) Voltage gated potassium; 3) '
               'Ligand[LIH-gund] gated sodium.',
          'a': 'JUST 2'},
         {'q': 'BIOLOGY Short Answer: In the spinal cord, cell bodies of sensory neurons are grouped together to form '
               'what structures?',
          'a': 'DORSAL ROOT GANGLIA'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three responses that are actions of the '
               'sympathetic nervous system: 1) Pupil constriction; 2) Increased heart rate; 3) Vasodilation '
               '[vay-zoh-dye-LAY-shun] in muscles.',
          'a': '2 AND 3'},
         {'q': 'BIOLOGY Multiple Choice: What aspect of a reaction does an enzyme change?\n'
               'W) Free energy\n'
               'X) Entropy [EN-troh-pee]\n'
               'Y) Enthalpy [EN-thul-pee]\n'
               'Z) Activation energy',
          'a': 'Z'},
         {'q': 'BIOLOGY Multiple Choice: What do amoebas use in order to move around?\n'
               'W) Cilia [SILL-ee-ah]\n'
               'X) Flagella [Flah-JEL-ah]\n'
               'Y) Pseudopodia [soo-dah-POH-dee-ah]\n'
               'Z) Asters',
          'a': 'Y'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following statements about monocots and dicots is NOT correct?\n'
               'W) Monocots have three holes in their pollen, while dicots only have one\n'
               'X) Monocots have scattered vascular bundles, while dicot bundles are in a ring\n'
               'Y) Monocots lack a pith region in the stem, while dicots have a pith\n'
               'Z) Monocots have parallel venation in their leaves while dicots have netted veins',
          'a': 'W'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following pairs of terms referring to the life cycle of land '
               'plants is mismatched with the correct ploidy?\n'
               'W) Megasporangium [mega-spor-AYN-gee-um] and diploid\n'
               'X) Sporocyte and diploid\n'
               'Y) Egg and haploid\n'
               'Z) Integument and haploid',
          'a': 'Z'},
         {'q': 'BIOLOGY Short Answer: What virus causes mononucleosis [mono-new-klee-OH-sis] in humans?',
          'a': 'EPSTEIN-BARR VIRUS'},
         {'q': 'BIOLOGY Short Answer: In a developing root, there are three regions: the region of cell division, the '
               'region of cell elongation, and the region of maturation. What external feature of the epidermis allows '
               'one to know they have located the region of maturation?',
          'a': 'ROOT HAIRS'},
         {'q': 'BIOLOGY Short Answer: What hormone targets the kidneys and stimulates reabsorption of water from '
               'urine?',
          'a': 'ADH'},
         {'q': 'BIOLOGY Short Answer: What thyroid hormone plays a role in inhibiting calcium loss from bones?',
          'a': 'CALCITONIN'},
         {'q': 'BIOLOGY Short Answer: What is the adjective for the type of nephron [NEF-ron] that possesses long '
               'loops of Henle\n'
               '[HEN-lee] in order to promote water reabsorption?',
          'a': 'JUXTAMEDULLARY'},
         {'q': 'BIOLOGY Short Answer: Rank the following four plasma proteins in terms of increasing mass:\n'
               '1) Fibrinogen [fye-BRIN-oh-jen]; 2) Transferrin [trans-FEH-rin]; 3) Albumin [al-BYOO-min];\n'
               '4) Immunoglobulin G [immune-oh-GLOB-yuh-lin G].',
          'a': '3, 2, 4, 1'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following scientific names correctly describes a family of '
               'plants?\n'
               'W) Quercus rubra\n'
               'X) Liliaceae [lilly-AY-see-eye]\n'
               'Y) Poales [Poh-AY-leez]\n'
               'Z) Magnoliophyta [mag-NO-lee-oh-FYE-tah]',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three statements that are true of second '
               'messengers:\n'
               '1) Phospholipase [faws-fo-LYE-pace] C catalyzes the release of IP3; 2) Cells store calcium in the '
               'nucleus;\n'
               '3) Calmodulin [kal-MOD-u-lin] binds to cyclic GMP.',
          'a': '1'},
         {'q': 'BIOLOGY Short Answer: Which animal phylum [FYE-lum] contains the most extant species?',
          'a': 'ARTHROPODA'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three nucleobases that are purines [PURE-eenz]: 1) '
               'Guanine\n'
               '[GWAH-neen]; 2) Uracil [YUR-ah-sil]; 3) Thymine [THIGH-meen].',
          'a': '1'},
         {'q': 'BIOLOGY Short Answer: What protein hormone, missing in obese mice with mutations in the ob [O.B.] '
               'gene, is responsible for controlling satiety [SAY-sha-tee]?',
          'a': 'LEPTIN'},
         {'q': 'BIOLOGY Short Answer: When fasting, the liver will convert amino acids to glucose. What is the name of '
               'this process?',
          'a': 'GLUCONEOGENESIS'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three genera [JEN-er-ah] of bacteria that are Gram '
               'positive:\n'
               '1) Escherichia [eh-sher-EE-kee-ah]; 2) Salmonella; 3) Vibrio [VIH-bree-oh].',
          'a': 'NONE'},
         {'q': 'BIOLOGY Short Answer: Identify the ploidy level for the following three plant life stages: 1) '
               'Sporophyte;\n'
               '2) Gametophyte; 3) Spore.',
          'a': '1) DIPLOID, 2) HAPLOID, 3) HAPLOID'},
         {'q': 'BIOLOGY Short Answer: What second messenger is produced by adenylyl [ah-DEN-il-il] cyclase '
               '[SIGH-klayse]?',
          'a': 'CYCLIC AMP'},
         {'q': 'BIOLOGY Short Answer: In a signalling pathway, a certain step requires the removal of a phosphate '
               'group from a protein. What general type of enzyme would perform this reaction?',
          'a': 'PHOSPHATASE'},
         {'q': 'BIOLOGY Short Answer: What enzyme is the major regulation site of glycolysis [glye-KAWL-eh-sis]?',
          'a': 'PHOSPHOFRUCTOKINASE'},
         {'q': 'BIOLOGY Short Answer: In glycolysis [glye-KAWL-eh-sis], what enzyme catalyzes the initial '
               'phosphorylation\n'
               '[faws-four-il-AY-shun] of glucose, preventing it from leaving the cell?',
          'a': 'HEXOKINASE'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following cell types is associated with haversian [ha-VER-zhen] '
               'canals?\n'
               'W) Osteocytes [AW-steo-sites]\n'
               'X) Chondrocytes [KON-droh-sites]\n'
               'Y) Fibroblasts\n'
               'Z) Leukocytes [LOO-koh-sites]',
          'a': 'W'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following four plants that have evolved mechanisms to reduce '
               'bio-energetically wasteful photorespiration: 1) Cactus; 2) Oak trees; 3) Potatoes; 4) Rice.',
          'a': '1'},
         {'q': 'BIOLOGY Short Answer: What is the genus [JEE-nus] of the harmless gut bacterium that can be '
               'transformed by a bacteriophage [bak-TEER-ee-oh-fayj] into a virulent [VEER-yoo-lent] form associated '
               'with cholera [CALL-ur-ah]?',
          'a': 'VIBRIO'},
         {'q': 'BIOLOGY Multiple Choice: A disease-linked, spontaneous, congenital [kon-GEH-nih-tul] germ line '
               'mutation creates a restriction site for HaeIII [HAY-three]. A diagnostic test for this mutation '
               'involves restriction digestion with endonuclease [en-doh-NEW-klee-ase] HaeIII. If the DNA of a patient '
               'with this mutation is tested and imaged using an agarose [AH-gah-rohs] gel, which of the following is '
               'expected?\n'
               'W) No diagnostic point mutation exists on either maternal or paternal chromosomes\n'
               'X) Both maternal and paternal chromosomes have the diagnostic point mutation\n'
               'Y) Either the maternal or the paternal chromosome has the point mutation, but not both\n'
               'Z) The test was inconclusive',
          'a': 'Y'},
         {'q': 'BIOLOGY Short Answer: What viral reproductive cycle kills the infected host cell while the virus is '
               'dividing?',
          'a': 'LYTIC CYCLE'},
         {'q': 'BIOLOGY Short Answer: What is the number of cells present in a mature male angiosperm gametophyte?',
          'a': '3'},
         {'q': 'BIOLOGY Short Answer: The Ti (tie) plasmid can be used to stably transfect some plants with '
               'recombinant DNA.\n'
               'What is the genus of the bacterium that is a vector for this plasmid?',
          'a': 'AGROBACTERIUM'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following four cell types involved in plant transport '
               'physiology that are non-living yet functional when mature: 1) Parenchyma [pah-REN-kimma]; 2) Sclereid '
               '[SKLAIR-ee-id]; 3) Sieve tube;\n'
               '4) Tracheid [TRAY-kee-id]',
          'a': '2 AND 4'},
         {'q': 'BIOLOGY Multiple Choice: Which of the following organisms possesses cnidocytes [NYE-doh-sites]?\n'
               'W) Tapeworm\n'
               'X) Jellyfish\n'
               'Y) Starfish\n'
               'Z) Sea cucumber',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: Rank the following four proteins in order of increasing oxygen-binding '
               'affinity:\n'
               '1) Adult hemoglobin at pH 7.4; 2) Fetal hemoglobin; 3) Adult hemoglobin at pH 7.2; 4) Myoglobin.',
          'a': '3, 1, 2, 4'},
         {'q': 'BIOLOGY Short Answer: What is the term for cancers that arise in epithelial [eh-pih-THEEL-ee-ul] '
               'tissues?',
          'a': 'CARCINOMA'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three statements that are true regarding tendrils '
               'in plants:\n'
               '1) They can only be found in dicot vines; 2) They can be modified stems, leaves, or flower stalks; 3) '
               'They are primarily used for climbing.',
          'a': '2 AND 3'},
         {'q': 'BIOLOGY Short Answer: From what group of organisms are restriction enzymes isolated?', 'a': 'BACTERIA'},
         {'q': 'BIOLOGY Short Answer: What storage polysaccharide that is found in animals contains highly branched '
               'chains of sugars containing 1, 4 and 1, 6 linkages?',
          'a': 'GLYCOGEN'},
         {'q': 'BIOLOGY Short Answer: What technique would scientists use if they wanted to amplify a small region of '
               'DNA?',
          'a': 'PCR'},
         {'q': 'BIOLOGY Short Answer: MPF, or mitosis [my-TOW-sis] promoting factor, is a complex between a CDK and a '
               'protein of what class?',
          'a': 'CYCLIN'},
         {'q': 'BIOLOGY Multiple Choice: The majority of speciation [spee-see-AY-shun] occurs under which of the '
               'following circumstances?\n'
               'W) When populations undergo sexual selection\n'
               'X) When populations become geographically separated\n'
               'Y) When populations are R selected\n'
               'Z) When populations reach carrying capacity',
          'a': 'X'},
         {'q': 'BIOLOGY Short Answer: A bacterial colony is raised in heavy nitrogen media for several generations, '
               'then transferred to a nitrogen-14 medium. Identify all of the following statements that will be true '
               'after one generation: 1) Half of the bacteria will have denser DNA than the other half; 2) Half of the '
               'bacteria will have no heavy nitrogen in their DNA;\n'
               '3) Half of the bacteria will have no nitrogen-14 in their DNA.',
          'a': 'NONE'},
         {'q': 'BIOLOGY Short Answer: Methylation [meth-il-AY-shun] of cytosine [sigh-toh-seen] was once thought to '
               'play an important role in repressing gene regulation. Deamination [dee-am-ih-NAY-shun] of\n'
               '5-methylcytosine [five methil-SYE-toh-seen] results in the production of what other nucleobase?',
          'a': 'THYMINE'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three disorders that are usually inherited '
               'dominantly:\n'
               '1) Huntington’s disease; 2) Albinism [AL-beh-nih-zim]; 3) Polydactyly [polly-DAK-til-ee].',
          'a': '1 AND 3'},
         {'q': 'BIOLOGY Short Answer: In E. coli, a certain gene undergoes a mutation such that the resulting protein '
               'is much larger in size and now non-functional. What type of mutation likely occurred?',
          'a': 'INSERTION'},
         {'q': 'BIOLOGY Short Answer: A scientist crosses a pea plant that is true breeding for the dominant traits of '
               'round and yellow seeds with a plant that is true breeding for wrinkled, green seeds. What fraction of '
               'the offspring will have round, green seeds?',
          'a': '0'},
         {'q': 'BIOLOGY Short Answer: What is the term for mobile elements of DNA that can cut and paste themselves '
               'into new locations?',
          'a': 'TRANSPOSONS'},
         {'q': 'BIOLOGY Short Answer: Identify all of the following three statements that are true regarding plant '
               'hormones:\n'
               '1) Auxin plays an important role in gravitropism; 2) Abscisic [ab-SIH-zik] acid inhibits primary and '
               'secondary growth; 3)\n'
               'Cytokinin [sigh-toh-KYE-nin] increases rate of leaf senescence [sen-EH-sense].',
          'a': '1 AND 2'}],
 'math': [{'q': 'MATH Multiple Choice: Matrices with which of the following pairs of dimensions cannot be multiplied '
                'together?\n'
                'W) 3 rows, 2 columns times 2 rows, 3 columns\n'
                'X) 6 rows, 5 columns times 6 rows, 5 columns\n'
                'Y) 1 row, 2 columns times 2 rows, 2 columns\n'
                'Z) 1,000 rows, 2,000 columns times 2,000 rows, 4,000 columns',
           'a': 'X'},
          {'q': 'MATH Short Answer: Evaluate the following expression: open parenthesis negative cosine\n'
                '360 degrees + sine 270 degrees close parenthesis times open parenthesis cosine 0 degrees + sine\n'
                '0 degrees close parenthesis squared.',
           'a': '–2'},
          {'q': 'MATH Short Answer: There are 8 siblings in a family, and when ranked from youngest to oldest, all '
                'differ from the next oldest in age by the same number of years. If the youngest is 8 and the oldest '
                'is 29, what is the common difference in their ages?',
           'a': '3'},
          {'q': 'MATH Multiple Choice: Following are four pairs of intersecting lines that are related to circles. For '
                'three of them, the measures of the angles formed can always be found by taking half of the difference '
                'of the angle measures of the intercepted arcs. For which does this calculation generally fail?\n'
                'W) Two tangents\n'
                'X) Two secants that intersect outside the circle\n'
                'Y) A tangent and a secant that intersect outside the circle\n'
                'Z) The lines containing two intersecting chords',
           'a': 'Z'},
          {'q': 'MATH Short Answer: What are the critical numbers for the function y = 3t3 – t?', 'a': '1/3, –1/3'},
          {'q': 'MATH Multiple Choice: Each day, Adam eats 20% of the cookies left in a jar. At the end of the 2nd '
                'day, there are 32 cookies left in the jar. How many cookies were in the jar originally?\n'
                'W) 40\n'
                'X) 48\n'
                'Y) 50\n'
                'Z) 60',
           'a': 'Y'},
          {'q': 'MATH Short Answer: How many lines of symmetry does a square have?', 'a': '4'},
          {'q': 'MATH Short Answer: What are the coordinates of the vertex of the graph of y = –2x2 – 8x + 7?',
           'a': ''},
          {'q': 'MATH Short Answer: What is the second derivative with respect to x of 2x3 – 12 evaluated at x = 3?',
           'a': '36'},
          {'q': 'MATH Short Answer: Solve the following equation for y: 3y minus open parenthesis 2 minus 2y close '
                'parenthesis plus 5 = 15 minus y.',
           'a': '2'},
          {'q': 'MATH Multiple Choice: If n is an integer, and xn is positive for all nonzero real numbers x, which of '
                'the following must be true about n?\n'
                'W) n is greater than zero\n'
                'X) n does not equal zero\n'
                'Y) n is even\n'
                'Z) n is odd',
           'a': 'Y'},
          {'q': 'MATH Multiple Choice: Which of the following points lies in the solution set for the following system '
                'of two inequalities in two unknowns: 3y – x ≥ –9 and 3y – 2x < –9?\n'
                'W) (3, 1)\n'
                'X) (4, –4)\n'
                'Y) (8, –2)\n'
                'Z) (8, 2)',
           'a': 'Z'},
          {'q': 'MATH Multiple Choice: When working with three coordinate axes, what rule determines the orientation '
                'of the z-axis in relation to the x- and y-axes?\n'
                'W) Left-hand rule\n'
                'X) Octant rule\n'
                'Y) Right-hand rule\n'
                'Z) Three-space rule',
           'a': 'Y'},
          {'q': 'MATH Short Answer: What number must be ADDED to both the numerator and denominator of 3/4 to get 4/3?',
           'a': '–7'},
          {'q': 'MATH Short Answer: How many points of intersection do the graphs of the functions f(x) = –x2 and g(x) '
                '= 2 raised to the x power have?',
           'a': '0'},
          {'q': 'MATH Short Answer: The terminal side of an angle in standard position passes through the point (8, '
                '–15). Find the sine and tangent, respectively, of the angle.',
           'a': 'SINE = –15/17, TANGENT = –15/8'},
          {'q': 'MATH Short Answer: What is the greatest common factor of 18 and 142?', 'a': '2'},
          {'q': 'MATH Multiple Choice: Which of the following points does the line 2x – 3y = –12 NOT pass through?\n'
                'W) (–2, 8/3)\n'
                'X) (1, –14/3)\n'
                'Y) (3, 6)\n'
                'Z) (7, 26/3)',
           'a': 'X'},
          {'q': 'MATH Short Answer: What is the discriminant of the quadratic function y = x2 – 4x + 10?', 'a': '-24'},
          {'q': 'MATH Short Answer: What is the derivative evaluated at x = 7 of the fraction with numerator x3 – 1 '
                'and denominator x – 1?',
           'a': '15'},
          {'q': 'MATH Short Answer: Evaluate the following expression: log base 3 of 27 + log base 5 of 25.', 'a': '5'},
          {'q': 'MATH Short Answer: What is the slope of the tangent line to the function\n'
                'F(x) = 1000 – 200x – 5x2 at x = 4?',
           'a': '-240'},
          {'q': 'MATH Short Answer: What is the value of 60 factorial divided by open parenthesis 59 factorial times 3 '
                'factorial close parenthesis?',
           'a': '10'},
          {'q': 'MATH Short Answer: Identify all of the following three integer operations that are commutative: 1) '
                'Addition; 2) Subtraction; 3) Multiplication.',
           'a': '1 AND 3'},
          {'q': 'MATH Short Answer: What is the midpoint of the segment with endpoints (1, 6) and (5, -2)?', 'a': ''},
          {'q': 'MATH Short Answer: Solve the following system of two equations in two unknowns: x2 + y2\n'
                '= 2 and x + y = 2.',
           'a': ''},
          {'q': 'MATH Short Answer: Specifying whether your answer is open or closed, what is the interval of angles '
                'in degrees whose terminal sides are in the second quadrant?',
           'a': 'THE OPEN INTERVAL FROM 90 TO 180'},
          {'q': 'MATH Multiple Choice: Which of the following base 2 sums is the largest?\n'
                'W) 1 + 1111 [one plus one one one one]\n'
                'X) 100 + 1001 [one zero zero plus one zero zero one]\n'
                'Y) 110 + 1000 [one one zero plus one zero zero zero]\n'
                'Z) 111 + 111 [one one one plus one one one]',
           'a': 'W'},
          {'q': 'MATH Short Answer: What is the limit as x approaches 3 of the function with numerator x –\n'
                '3 and denominator x2 – 9?',
           'a': '1/6'},
          {'q': 'MATH Short Answer: Special water for a 600-liter aquarium is only sold in 35-liter containers. What '
                'is the minimum number of these 35-liter containers you would need to buy to be able to completely '
                'fill the tank?',
           'a': '18'},
          {'q': 'MATH Short Answer: Given f(x) = 3x – 5 and g(x) = 4x, what is f of g of x?', 'a': '12x – 5'},
          {'q': 'MATH Short Answer: What is the least common multiple of the first four composite numbers?', 'a': '72'},
          {'q': 'MATH Short Answer: The ratio of the measures of the three angles in a triangle is 2:3:4. What are the '
                'degree measures of the three angles?',
           'a': '40, 60, 80'},
          {'q': 'MATH Short Answer: What mathematical rule can be applied to give information about the number of '
                'positive or negative real roots of a polynomial based on the number of sign changes in the '
                'polynomial’s coefficients?',
           'a': 'DESCARTES’ RULE OF SIGNS'},
          {'q': 'MATH Multiple Choice: With respect to x, which of the following has –3x2 as an antiderivative?\n'
                'W) –6x\n'
                'X) 6x\n'
                'Y) –x3\n'
                'Z) x3',
           'a': 'W'},
          {'q': 'MATH Short Answer: Identify the center and radius of the sphere with equation 36 = open parenthesis x '
                '– 2 close parenthesis squared + open parenthesis y – 7 close parenthesis squared + open parenthesis z '
                '+ 1 close parenthesis squared.',
           'a': 'CENTER'},
          {'q': 'MATH Short Answer: What are the prime factors of 105?', 'a': '3, 5, and 7'},
          {'q': 'MATH Multiple Choice: If f(x) = the square root of open parenthesis x + 3 close parenthesis and g(x) '
                '= the square root of open parenthesis x – 3 close parenthesis, what is the domain of the function '
                'f(x) divided by g(x)?\n'
                'W) x > 3\n'
                'X) x ≥ 3\n'
                'Y) x ≥ -3\n'
                'Z) -3 < x < 3',
           'a': 'W'},
          {'q': 'MATH Short Answer: How many exterior angles does a parallelogram have?', 'a': '8'},
          {'q': 'MATH Short Answer: What is the sum from n = 1 to 4 of 2n2?', 'a': '60'},
          {'q': 'MATH Short Answer: What is the degree measure of each interior angle in a regular hexagon?',
           'a': '120'},
          {'q': 'MATH Multiple Choice: Which of the following is true regarding the graph of y = –x3 at x = –2?\n'
                'W) increasing and concave up\n'
                'X) increasing and concave down\n'
                'Y) decreasing and concave up\n'
                'Z) decreasing and concave down',
           'a': 'Y'},
          {'q': 'MATH Multiple Choice: Which of the following equations is that of a line perpendicular to the line '
                'with equation 4x – 5y = 10?\n'
                'W) 4x – 5y = 12\n'
                'X) 4x + 5y = 12\n'
                'Y) 5x – 4y = 10\n'
                'Z) 5x + 4y = 10',
           'a': 'Z'},
          {'q': 'MATH Short Answer: Identify all of the following four properties that are preserved under a '
                'translation: 1) Distance; 2) Collinearity; 3) Midpoint; 4) Angle measure.',
           'a': '1, 2, 3, 4'},
          {'q': 'MATH Short Answer: What is the degree of the polynomial x2 + 3x8 + 7x?', 'a': '8'},
          {'q': 'MATH Short Answer: Maggie bakes 48 cookies and sells half of them that morning for $2.50 each. In the '
                'afternoon, she sells two-thirds of what she has left at half price. In the late afternoon, she sells '
                'the remaining cookies at a dollar each. If each cookie costs 75 cents for her to make, what was her '
                'profit, in dollars, for the day?',
           'a': '52'},
          {'q': 'MATH Short Answer: The complex number –4 lies on the boundary between what two quadrants in the '
                'complex plane?',
           'a': '2 AND 3'},
          {'q': 'MATH Short Answer: Solve the following equation for x: negative 8 plus the absolute value of open '
                'parenthesis 4 minus 3x close parenthesis equals 20.',
           'a': '–8, 32/3'},
          {'q': 'MATH Short Answer: What is binary one-zero-zero-one in decimal form?', 'a': '9'},
          {'q': 'MATH Short Answer: Perform the following complex number subtraction: –4 – 25i subtracted from –11 – '
                '7i.',
           'a': '–7 + 18i'},
          {'q': 'MATH Multiple Choice: For a twice-differentiable function f(x), f(3) is 4, f prime of 3 is 0 and f '
                'double prime of 3 is 5. Which of the following is true of the graph of y = f(x) at the point (3,\n'
                '4)?\n'
                'W) There is a local minimum\n'
                'X) There is a local maximum\n'
                'Y) There is an inflection point\n'
                'Z) The graph is concave down',
           'a': 'W'},
          {'q': 'MATH Short Answer: Find the circumference of a circle with area equal to one over pi.', 'a': '2'},
          {'q': 'MATH Short Answer: What is the sine of 270 degrees?', 'a': '–1'},
          {'q': 'MATH Short Answer: Give the Cartesian coordinates of the point described by the cylindrical '
                'coordinates (r, theta, h) = (8, π/3, 24).',
           'a': ''},
          {'q': 'MATH Short Answer: Giving your answer in standard form, what is the equation of the circle with '
                'center at (0, 0) and diameter 10?',
           'a': 'x2 + y2 = 25'},
          {'q': 'MATH Multiple Choice: What is 4 to the power of log base 2 of 5?\n'
                'W) 1/5\n'
                'X) Square root of 5\n'
                'Y) 5\n'
                'Z) 25',
           'a': 'Z'},
          {'q': 'MATH Multiple Choice: Given sets A and B with A intersect B = the set containing the element 5, which '
                'of the following must be true?\n'
                'W) Set A may be the empty set\n'
                'X) Set A contains at least one element\n'
                'Y) Set B contains at most one element\n'
                'Z) Sets A and B have the same number of elements',
           'a': 'X'},
          {'q': 'MATH Short Answer: Expressing your answer in terms of m, evaluate the function f(x) = 4x2 – 9x + 11 '
                'when x is m – 7.',
           'a': '4m2 – 65m + 270'},
          {'q': 'MATH Short Answer: What is the sum of the two vectors 7i + 3j and 2i – 5j?', 'a': '9i – 2j'},
          {'q': 'MATH Short Answer: The perimeters of two squares differ by 16 inches and their areas differ by 96 '
                'square inches. What is the perimeter, in inches, of the larger square?',
           'a': '56'},
          {'q': 'MATH Short Answer: What is the distance between the points (0, 1) and (2, 3)?', 'a': '2√2'},
          {'q': 'MATH Short Answer: What is the sum from n = 0 to 2016 of the cosine of open parenthesis pi times n '
                'divided by 2 close parenthesis?',
           'a': '1'},
          {'q': 'MATH Short Answer: What is the fourth term in the series given by the sum from n = 0 to infinity of '
                'the fraction with numerator 1 and denominator 2 to the nth power?',
           'a': '1/8'},
          {'q': 'MATH Short Answer: Evaluate 112 + 212 + 312.', 'a': '1523'},
          {'q': 'MATH Short Answer: What is the integral from –6 to 6 of 6 dx?', 'a': '72'},
          {'q': 'MATH Short Answer: One endpoint of a diameter of a sphere centered at (4, 2, –9) is (5, –6,\n'
                '2). What are the coordinates of the other endpoint of that diameter?',
           'a': ''},
          {'q': 'MATH Short Answer: How many terms does the binomial expansion of open parenthesis x2 +\n'
                '3y3 close parenthesis to 13th power contain?',
           'a': '14'},
          {'q': 'MATH Short Answer: A right triangle has hypotenuse of length 46 and one leg of length 44.\n'
                'What is the length of the third side?',
           'a': '6√5'},
          {'q': 'MATH Short Answer: If the graph of y equals open parenthesis x minus two close parenthesis squared '
                'minus three is translated 6 units up and 3 units to the right, what are the coordinates of the vertex '
                'of the image?',
           'a': ''},
          {'q': 'MATH Short Answer: A bag contains 18 socks: 4 are red, 6 are white, and 8 are blue. How many socks '
                'must you take out to be certain that you will have at least one pair of blue socks?',
           'a': '12'},
          {'q': 'MATH Short Answer: What is the slope of the line with equation 5x + 3y = 8?', 'a': '–5/3'},
          {'q': 'MATH Short Answer: The three sides of a triangle have lengths 4 centimeters, 6 centimeters, and 7 '
                'centimeters. What is the cosine of the smallest angle?',
           'a': '23/28'},
          {'q': 'MATH Short Answer: What is the determinant of the 2 by 2 matrix with first row –2, –3 and second row '
                '8, –4?',
           'a': '32'},
          {'q': 'MATH Multiple Choice: What is the probability that the bottom card in a deck of cards is a queen and '
                'the top card is a king?\n'
                'W) 1/169\n'
                'X) 4/663\n'
                'Y) 5/663\n'
                'Z) 1/2702',
           'a': 'X'},
          {'q': 'MATH Short Answer: What is the complex conjugate of –4 – 36i?', 'a': '–4 + 36i'},
          {'q': 'MATH Short Answer: What are the radius and the coordinates of the center, respectively, of the circle '
                'with equation x2 + 8x + y2 – 6y = 0?',
           'a': 'RADIUS 5; CENTER'},
          {'q': 'MATH Short Answer: What is the derivative with respect to x of -5 divided by x6?', 'a': '30/x7'},
          {'q': 'MATH Short Answer: What are the linear factors of the polynomial 2ab + 3a – 8b – 12?',
           'a': 'a – 4 AND 2b + 3'},
          {'q': 'MATH Short Answer: If all of the prime factors of 444, including multiple occurences, are added, how '
                'much greater will the result be than that for 222?',
           'a': '2'},
          {'q': 'MATH Short Answer: Two circles with radii of 3 inches and 1 inch have the same center.\n'
                'What is the ratio of the area of the annulus between the inner circle and the outer circle to the '
                'area of the inner circle?',
           'a': '8'},
          {'q': 'MATH Multiple Choice: Let f(x) be a continuous and differentiable function on the closed interval '
                '[3,6]. Which of the following could be the x-value guaranteed by the Mean Value Theorem for this '
                'situation?\n'
                'W) 2\n'
                'X) 3\n'
                'Y) 5\n'
                'Z) 7',
           'a': 'Y'},
          {'q': 'MATH Short Answer: One dimension of a cube is increased by 1, another is decreased by 1, and the '
                'other is left unchanged. If the new solid has a volume 5 less than that of the original cube, what '
                'was the volume of the original cube?',
           'a': '125'},
          {'q': 'MATH Short Answer: How many points of intersection are there for the graphs of y = 3x and y = –x2 + '
                '5?',
           'a': '2'},
          {'q': 'MATH Multiple Choice: Which of the following is nearest to 1,000,000?\n'
                'W) 5 to the 6th power\n'
                'X) 10 to the 7th power\n'
                'Y) 2 to the 20th power\n'
                'Z) 400 squared',
           'a': 'Y'},
          {'q': 'MATH Short Answer: Identify all of the four quadrants in which cosecant is positive.', 'a': '1 and 2'},
          {'q': 'MATH Short Answer: What is the image of the point (0, 0) when it is reflected across the line y = x – '
                '1?',
           'a': ''},
          {'q': 'MATH Short Answer: If n is an odd integer, how many lines of symmetry does a regular n- gon have?',
           'a': 'n'},
          {'q': 'MATH Short Answer: Solve the following equation for x over the real numbers: 8 to the power open '
                'parenthesis 2x close parenthesis equals 4 to the power open parenthesis 2x minus 1 close parenthesis.',
           'a': '–1'},
          {'q': 'MATH Multiple Choice: Which of the following best describes the type of conic section represented by '
                'the equation x2 + 10x + y2 + 16 equals zero?\n'
                'W) Circle\n'
                'X) Ellipse\n'
                'Y) Hyperbola\n'
                'Z) Parabola',
           'a': 'W'},
          {'q': 'MATH Short Answer: If the third derivative of a position function can be described by the function '
                '4t, what is the coefficient on the highest order term in the position function?',
           'a': '1/6'},
          {'q': 'MATH Multiple Choice: Which of the following is equivalent to cosine56°cosine23° – sine23°sine56°?\n'
                'W) sine 33°\n'
                'X) cosine 33°\n'
                'Y) sine 79°\n'
                'Z) cosine 79°',
           'a': 'Z'},
          {'q': 'MATH Short Answer: What are the mean and the median, respectively, of the prime numbers less than 25?',
           'a': 'MEAN 100/9'},
          {'q': 'MATH Short Answer: If an exterior angle adjacent to a base angle of an isosceles [eye-SOSS- uh-lees] '
                'triangle measures 132º, what is the degree measure of the vertex angle?',
           'a': '84'},
          {'q': 'MATH Multiple Choice: According to the rational root theorem, which of the following is\n'
                'NOT a possible solution to the equation x3 – 2x2 + x – 2 = 0?\n'
                'W) –1\n'
                'X) ½\n'
                'Y) 1\n'
                'Z) 2',
           'a': 'X'},
          {'q': 'MATH Short Answer: What is the 4th term of the geometric series with first term 400 and second term '
                '120?',
           'a': '10.8'},
          {'q': 'MATH Short Answer: Simplify the following expression involving the complex number i: i + 2i2 + 3i3 + '
                '4i4',
           'a': '2 – 2i'},
          {'q': 'MATH Short Answer: What is the sum of the largest prime number less than 50 and the largest prime '
                'number less than 100?',
           'a': '144'},
          {'q': 'MATH Short Answer: The bob on a pendulum swings through an arc 6 feet long when the string swings '
                'through an angle of 0.5 radians. What is the length of the pendulum in feet?',
           'a': '12'},
          {'q': 'MATH Multiple Choice: In the conversion of the rectangular coordinates (-8, 6) into polar '
                'coordinates, to the nearest whole number, what is the degree measure of the angle?\n'
                'W) 127\n'
                'X) 143\n'
                'Y) 307\n'
                'Z) 323',
           'a': 'X'},
          {'q': 'MATH Short Answer: What is the area, in square centimeters, of an equilateral triangle whose '
                'circumcircle has a radius of 10 centimeters?',
           'a': '75√3'},
          {'q': 'MATH Short Answer: What is the product of the complex numbers 3 + i and 2 + 3i?', 'a': '3 + 11i'},
          {'q': 'MATH Short Answer: What is the remainder when 3x3 + 6x2 – 7x + 2 is divided by the binomial x + 4?',
           'a': '-66'},
          {'q': 'MATH Short Answer: A special coin has a 1/3 probability of landing on heads, and a 2/3 probability of '
                'landing on tails. In a series of three coin flips, what is the probability of the outcome sequence '
                'heads, heads, tails?',
           'a': '2/27'},
          {'q': 'MATH Short Answer: What is the average value of the function f(x) = x2 over the interval –2 to 2?',
           'a': '4/3'},
          {'q': 'MATH Multiple Choice: Let f(x) be a polynomial function with real coefficients and at least one real '
                'root. Which of the following must be true?\n'
                'W) f(x) has an even number of non-real complex roots\n'
                'X) f(x) is of odd degree\n'
                'Y) f(x) is an even function\n'
                'Z) The graph of f(x) has a horizontal asymptote',
           'a': 'W'},
          {'q': 'MATH Short Answer: A square has sides of length 10 centimeters. In square centimeters, what is the '
                'difference between the areas of its circumscribing circle and its inscribed circle?',
           'a': '25π'},
          {'q': 'MATH Multiple Choice: Which of the following equations does NOT include the half-line y\n'
                '= x, where x and y are positive, in its solution set?\n'
                'W) xy = yx\n'
                'X) cosine of the product xy equals sine of the product xy\n'
                'Y) x natural log of y = y natural log of x\n'
                'Z) 2x + 3y = 2y + 3x',
           'a': 'X'},
          {'q': 'MATH Short Answer: A national achievement test is administered. The test has a mean score of 100 and '
                'a standard deviation of 10. If Ann’s Z-score is –1.3, what is her score on the test?',
           'a': '87'},
          {'q': 'MATH Multiple Choice: Given two sets A and B with A union B containing exactly 3 elements, which of '
                'the following must be true about sets A and B?\n'
                'W) Each set contains at least 2 elements\n'
                'X) Each set contains at most 2 elements\n'
                'Y) Each set contains at least 3 elements\n'
                'Z) Each set contains at most 3 elements',
           'a': 'Z'},
          {'q': 'MATH Short Answer: What is the area between the curves y = x + 3 and y = x3 between x = 0 and x = 1?',
           'a': '13/4'},
          {'q': 'MATH Short Answer: What is the log base 3 of 729?', 'a': '6'},
          {'q': 'MATH Short Answer: A restaurant’s 4 dollar box allows you to pick any 2 of 4 possible entrees '
                '(including 2 of the same), one of 2 sides, one of 2 desserts, and one of 3 drinks. How many different '
                'orders are possible?',
           'a': '120'},
          {'q': 'MATH Multiple Choice: Which of the following is the contrapositive of the conditional statement: If '
                'p, then q?\n'
                'W) If q, then p\n'
                'X) If not p, then q\n'
                'Y) If not p, then not q\n'
                'Z) If not q, then not p',
           'a': 'Z'},
          {'q': 'MATH Short Answer: What is the area of a triangle with sides of length 11, 8, and 5?', 'a': '4√21'},
          {'q': 'MATH Short Answer: If theta is an angle in the third quadrant and the cosine of theta equals negative '
                'five-thirteenths, what is the sine of theta?',
           'a': '-12/13'},
          {'q': 'MATH Short Answer: Express the fraction with numerator 3 – 2i and denominator 1 + 4i in standard a + '
                'bi form.',
           'a': '–5/17 –'},
          {'q': 'MATH Short Answer: If y varies jointly with x and z, and y = 12 when x = 4 and z = 5, find y when x = '
                '20 and z = 4.',
           'a': 'y = 48'},
          {'q': 'MATH Short Answer: What is the standard deviation of the following list of 4 numbers: 3,\n3, 9, 17?',
           'a': 'SQUARE ROOT OF 33'},
          {'q': 'MATH Short Answer: What is the dot product of 4i – 6j and –3i + j?', 'a': '–18'},
          {'q': 'MATH Short Answer: Find the volume of the solid obtained by rotating about the y-axis the region '
                'bounded by y = x – x4 and y = 0.',
           'a': 'π/3'},
          {'q': 'MATH Multiple Choice: Which of the following describes the solutions for the equation x to the x '
                'power = x to the x + 1 power?\n'
                'W) –1 and 1\n'
                'X) 0\n'
                'Y) 1\n'
                'Z) No solution exists',
           'a': 'Y'},
          {'q': 'MATH Short Answer: What is the sum of the first 6 terms in the geometric sequence with first term 3 '
                'and second term 12?',
           'a': '4095'},
          {'q': 'MATH Short Answer: The point (3, –7) is reflected through the y-axis, with the result then translated '
                '2 units left. What are the coordinates of the final image?',
           'a': ''},
          {'q': 'MATH Short Answer: What is the distance between the two points with polar coordinates of r = 4 and '
                'theta = 60 degrees, and r = 6 and theta = 0 degrees?',
           'a': '2√7'},
          {'q': 'MATH Short Answer: What is the average of the integers from 1 to 21, inclusive?', 'a': '11'},
          {'q': 'MATH Short Answer: If air leaves a spherical balloon at a rate of 1 cubic centimeter per second, at '
                'what rate in centimeters per second is the radius changing when the radius is 1/2 centimeter?',
           'a': '–1/pi'},
          {'q': 'MATH Short Answer: Simplify i raised to the 22nd power.', 'a': '–1'},
          {'q': 'MATH Short Answer: In a circle with radius 4, what is the area of a circular segment defined by an '
                'arc of 45°?',
           'a': '2pi - 4√2'}, {'q': 'MATH Short Answer: Giving your answer as a decimal, increasing a number by 250% is equivalent to '
                'multiplying it by what?',
           'a': '3.5'},
          {'q': 'MATH Short Answer: A rhombus has a diagonal of length 14 and a perimeter of 48. What is the length of '
                'the other diagonal?',
           'a': '2√95'},
          {'q': 'MATH Short Answer: What is the distance between the points (–1, 2) and (–10, 9)?', 'a': '√130'},
          {'q': 'MATH Short Answer: Identify all of the following 3 numbers that are evenly divisible by eight:\n'
                '1) 3,247,456; 2) 4,693,532; 3) 789,152.',
           'a': '1 and 3'},
          {'q': 'MATH Short Answer: Solve the following equation for x: log base 3 of open parenthesis x + 5 close '
                'parenthesis = 4?',
           'a': '76'},
          {'q': 'MATH Short Answer: If cosine of x times sine of x equals 1/5, what is the value of open parenthesis '
                'cosine of x minus sine of x close parenthesis squared?',
           'a': '3/5'},
          {'q': 'MATH Short Answer: Express as a fraction the repeating decimal 0.181818, with repeating part '
                'one-eight.',
           'a': '2/11'},
          {'q': 'MATH Short Answer: What is the slope-intercept equation of the line tangent to the graph of y = x3 + '
                'x2 at the point (1,2)?',
           'a': 'y = 5x – 3'},
          {'q': 'MATH Short Answer: In a room of 12 people, two meet for a handshake. How many different such meetings '
                'could take place?',
           'a': '66'},
          {'q': 'MATH Short Answer: If x is inversely proportional to y2 and if x = 3 when y = 4, what is the value of '
                'x when y = 6?',
           'a': '4/3'},
          {'q': 'MATH Short Answer: If a equals 6 cosine theta and b equals 6 sine theta, what is the square root of '
                'open parenthesis a2 + b2 close parenthesis?',
           'a': '6'},
          {'q': 'MATH Short Answer: What is the median of the set of the first 2017 even positive integers?',
           'a': '2018'},
          {'q': 'MATH Short Answer: How many faces does a hexagonal pyramid have?', 'a': '7'},
          {'q': 'MATH Short Answer: Two dice are rolled. What is the probability that the results are the same or that '
                'the sum is 8?',
           'a': '5/18'},
          {'q': 'MATH Short Answer: What is 4 times 3 squared?', 'a': '36'},
          {'q': 'MATH Short Answer: Johnny is asked by his teacher to subtract 4 from a number and multiply the result '
                'by 5.\n'
                'Instead, he subtracts 5 and then multiplies the result by 4, giving him 168. What is the correct '
                'answer to the teacher’s question?',
           'a': '215'},
          {'q': 'MATH Multiple Choice: The natural log of which of the following is irrational?\n'
                'W) 1\n'
                'X) √e\n'
                'Y) e\n'
                'Z) 10',
           'a': 'Z'},
          {'q': 'MATH Short Answer: If two sides of a right triangle have lengths 13 and 7, then, rounded to the '
                'nearest whole numbers, what are the possible lengths of the third side?',
           'a': '11 and 15'},
          {'q': 'MATH Short Answer: What is the x-coordinate of the vertex of the parabola with equation y = 6x2 + 4x '
                '– 7?',
           'a': '–1/3'},
          {'q': 'MATH Short Answer: During football season, a player catches passes for 687 yards and averages 14.6 '
                'yards per catch, rounded to the nearest tenth. How many catches did the player make?',
           'a': '47'},
          {'q': 'MATH Short Answer: What is 145 squared?', 'a': '21,025'},
          {'q': 'MATH Short Answer: For what values of x does the function f of x = the fraction with numerator x2 – '
                '25 and denominator 3x2 – 16x + 5 have a vertical asymptote?',
           'a': '1/3'},
          {'q': 'MATH Short Answer: 3 is one-third percent of what number?', 'a': '900'},
          {'q': 'MATH Short Answer: For real numbers a and b, define the binary operation “star” by a “star” b is '
                'equal to one less than the average of a and b. What is 3 “star” open parenthesis 4 “star” 5 close '
                'parenthesis?',
           'a': '9/4'},
          {'q': 'MATH Multiple Choice: A and B are statements, and B is false. Which of the following is true '
                'regarding the statement "B implies A?"\n'
                'W) It is true regardless of the truth value of A\n'
                'X) It is false regardless of the truth value of A\n'
                'Y) It is true only when A is true and false otherwise\n'
                'Z) It is true only when A is false and false otherwise',
           'a': 'W'},
          {'q': 'MATH Short Answer: The line with equation y = 5x + 4 is reflected across the line y = x. What are the '
                'slope and y-intercept of its image, respectively?',
           'a': 'SLOPE = 1/5, y-INTERCEPT = –4/5'},
          {'q': 'MATH Short Answer: A one-to-one function has its graph in the second quadrant. In which quadrant will '
                'the graph of its inverse lie?',
           'a': 'FOURTH'},
          {'q': 'MATH Short Answer: If the line tangent to the graph of the differentiable function f of x at the '
                'point (–2, 5) passes through the point (3.5, –3), then what is value of the derivative of f of x when '
                'x = –2?',
           'a': '–16/11'},
          {'q': 'MATH Short Answer: What is 4/9 divided by 8/15?', 'a': '5/6'},
          {'q': 'MATH Short Answer: What are the radius and the coordinates of the center of the circle with equation '
                'x2 – 14x + y2 + 8y + 41 = 0?',
           'a': 'RADIUS = 2√6, CENTER ='},
          {'q': 'MATH Short Answer: Name one of the linear factors of x2 + 14x – 72.', 'a': 'x – 4 OR x + 18'},
          {'q': 'MATH Short Answer: What is the sum of the distinct prime factors of 348?', 'a': '34'},
          {'q': 'MATH Multiple Choice: Two coplanar circles have a common chord. Which of the following best describes '
                'the quadrilateral that has as opposite vertices the centers of the two circles and the endpoints of '
                'the common chord?\n'
                'W) Kite\n'
                'X) Parallelogram\n'
                'Y) Rhombus\n'
                'Z) Square',
           'a': 'W'},
          {'q': 'MATH Short Answer: A particle’s position x at time t is defined by the equation x of t = 2t 3 – 21t 2 '
                '+ 60t – 36. At what time or times t is the particle at rest?',
           'a': '2 AND 5'},
          {'q': 'MATH Short Answer: A prism with 7 faces has how many edges?', 'a': '15'},
          {'q': 'MATH Short Answer: Evaluate the summation, from n = 0 to infinity, of the fraction with numerator 12 '
                'and denominator 4n.',
           'a': '16'},
          {'q': 'MATH Short Answer: What is the log base 3 of 243?', 'a': '5'},
          {'q': 'MATH Short Answer: What is the integer part of the geometric mean of 6 and 80?', 'a': '21'},
          {'q': 'MATH Short Answer: What is the slope of the line with equation 3x – 8y = –24?', 'a': '3/8'},
          {'q': 'MATH Short Answer: A class of 16 students selects a different student of the month each month during '
                'March,\n'
                'April, and May. In how many different ways can the 3 honored students be selected?',
           'a': '3360'},
          {'q': 'MATH Multiple Choice: A differentiable function f has domain the closed interval from –3 to 4 and '
                'range the closed interval from 5 to 12. If f prime of x is greater than 0 for all x in the domain, '
                'what is f of –3?\n'
                'W) –3\n'
                'X) 4\n'
                'Y) 5\n'
                'Z) 12',
           'a': 'Y'},
          {'q': 'MATH Short Answer: How many two-digit positive integers do NOT have 5 or 6 as a digit?', 'a': '56'},
          {'q': 'MATH Short Answer: What is the period of the function with equation y = 4 sine open parenthesis 7x + '
                '3 close parenthesis + 2?',
           'a': '2π/7'},
          {'q': 'MATH Short Answer: What is the area in the first quadrant between the graphs of y = 4x and y = x3?',
           'a': '4'},
          {'q': 'MATH Short Answer: In what quadrants does the graph of the equation y = 4x – 3 lie?',
           'a': '1, 3, AND 4'},
          {'q': 'MATH Short Answer: What is the least common multiple of 14, 16, and 18?', 'a': '1008'},
          {'q': 'MATH Short Answer: What is 62 – 26?', 'a': '–28'},
          {'q': 'MATH Short Answer: Solve the following equation for x over the negative integers: x3 + 5x2 – 4x – 20 '
                '= 0',
           'a': '–2 AND –5'},
          {'q': 'MATH Short Answer: If f is a continuous function such that the definite integral from 3 to 7 of f of '
                'x dx equals 14, what is the average value of f on the closed interval from 3 to 7?',
           'a': '7/2'},
          {'q': 'MATH Short Answer: How many sides does a regular polygon have if each interior angle measures 177 '
                'degrees?',
           'a': '120'},
          {'q': 'MATH Short Answer: A triangle has two sides of lengths 38 and 54. What is the largest possible '
                'integer length of the third side?',
           'a': '91'},
          {'q': 'MATH Short Answer: When applying the Euclidean algorithm to find the greatest common divisor of 42 '
                'and 157, what is the remainder after the third step?',
           'a': '9'},
          {'q': 'MATH Short Answer: What is the –4/3 power of –27?', 'a': '1/81'},
          {'q': 'MATH Short Answer: What is the limit as x approaches 0 of the fraction with numerator ex – 1 and '
                'denominator x5?',
           'a': 'INFINITY'},
          {'q': 'MATH Short Answer: A pyramid with 14 edges has how many vertices?', 'a': '8'},
          {'q': 'MATH Short Answer: A plane is traveling at 380 miles per hour with respect to the Earth. The Sun’s '
                'reflection off the plane illuminates a small area on the surface of the Earth. A passenger on the '
                'plane observes this illuminated spot move between two houses in 12 seconds. To the nearest tenth of a '
                'mile, how far apart are the two houses?',
           'a': '1.3'},
          {'q': 'MATH Short Answer: Find the value of x for which the following vectors are parallel:\n'
                '4i − 3j and xi + 12j.',
           'a': '–16'},
          {'q': 'MATH Short Answer: Consider a pair of “loaded” six-sided dice. In this case, each die is weighted so '
                'that a one is rolled one-third of the time. The other numbers are all still equally likely. What is '
                'the probability of rolling a pair of sixes?',
           'a': '4/225'},
          {'q': 'MATH Short Answer: If f of x equals the cube root of open parenthesis x – 6 close parenthesis, what '
                'is f inverse of 5?',
           'a': '131'},
          {'q': 'MATH Short Answer: Simplify cosine open parenthesis x – π/4 close parenthesis + sine open parenthesis '
                'x – π/4 close parenthesis.',
           'a': ''},
          {'q': 'MATH Short Answer: What is the partial derivative with respect to y of the expression x5y4?',
           'a': '4x5y3'},
          {'q': 'MATH Short Answer: What is the units digit of 8 to the 88th power?', 'a': '6'},
          {'q': 'MATH Short Answer: In base 7, what is 4 + 6?', 'a': 'ONE-THREE'},
          {'q': 'MATH Short Answer: Evaluate the integral from x = –8 to 0 of the square root of open parenthesis 64 – '
                'x2 close parenthesis dx.',
           'a': '16π'},
          {'q': 'MATH Short Answer: What is the area of a kite with diagonals of lengths 5 and 8?', 'a': '20'},
          {'q': 'MATH Short Answer: If a sub one = 3 and, for n greater than one, a sub n = 2 a sub n–1 minus 1, what '
                'is the value of a sub five?',
           'a': '33'},
          {'q': 'MATH Multiple Choice: The graph of a continuous function f contains the points (4, –5) and (7, –1). '
                'The intermediate value theorem guarantees an x-value such that f of x equals which of the following?\n'
                'W) –6\n'
                'X) –2\n'
                'Y) 2\n'
                'Z) 6',
           'a': 'X'},
          {'q': 'MATH Short Answer: How many positive integral factors does 936 have?', 'a': '24'},
          {'q': 'MATH Short Answer: What is the dot product of the vectors 4i – 2j + k and 3i – k?', 'a': '11'},
          {'q': 'MATH Short Answer: An isosceles trapezoid with integer side lengths has bases of length 12 and 26. '
                'What is the minimum length of its shortest side?',
           'a': '8'},
          {'q': 'MATH Short Answer: If the difference between two prime numbers is 27, what is their sum?', 'a': '31'},
          {'q': 'MATH Short Answer: A custom mixture of nuts is composed of cashews worth $16 a pound and almonds '
                'worth $10 a pound. May purchases 8 pounds of the mixture for $113. How many of these 8 pounds are '
                'cashews?',
           'a': '5.5'},
          {'q': 'MATH Multiple Choice: Consider the polynomial equation 6x3 – 20x + 15 = 0. According to the rational '
                'root theorem, which of the following is NOT a possible rational root of this equation?\n'
                'W) –5\n'
                'X) 1/3\n'
                'Y) 1/2\n'
                'Z) 6/5',
           'a': 'Z'},
          {'q': 'MATH Short Answer: If the sides of a triangle have lengths 5, 7, and 8, what is the cosine of the '
                'largest angle?',
           'a': '1/7'},
          {'q': 'MATH Short Answer: If angle ABC is inscribed in a circle and measures 15 degrees, what is the degree '
                'measure of arc ABC?',
           'a': '330'},
          {'q': 'MATH Short Answer: A triangular right prism has each edge of length 10. To the nearest ten, what is '
                'its volume?',
           'a': '430'},
          {'q': 'MATH Short Answer: To the nearest whole number, what is the slant height of a right circular cone '
                'with radius 6 and height 9?',
           'a': '11'},
          {'q': 'MATH Short Answer: How many zeros occur at the right of the number of permutations of 100 objects '
                'taken 80 at a time?',
           'a': '5'},
          {'q': 'MATH Short Answer: In base 8, what is 6 times 7?', 'a': 'FIVE-TWO'},
          {'q': 'MATH Short Answer: Rounded to the nearest integer, what is the area of a circle of circumference 15?',
           'a': '18'},
          {'q': 'MATH Multiple Choice: Given that the function f of x has a zero at x = 6, at what x-value must 2 + f '
                'of x have a zero?\n'
                'W) 3\n'
                'X) 4\n'
                'Y) 8\n'
                'Z) It need not have a zero',
           'a': 'Z'},
          {'q': 'MATH Short Answer: What is the real quadratic polynomial with least possible positive integer leading '
                'coefficient that has 7 – 8i as a zero?',
           'a': 'x2 – 14x + 113'},
          {'q': 'MATH Short Answer: What is the greatest integer that is less than or equal to the log base 6 of 975?',
           'a': '3'},
          {'q': 'MATH Short Answer: To the nearest degree, what is the measure of each interior angle of a regular '
                '65-sided polygon?',
           'a': '174'},
          {'q': 'MATH Short Answer: If the definite integral from 1 to 6 of f of x dx = 21, then what is the definite '
                'integral from 1 to 6 of open parenthesis f of x minus 3 close parenthesis dx?',
           'a': '6'},
          {'q': 'MATH Short Answer: What is the sum of the squares of the first 20 positive integers?', 'a': '2870'},
          {'q': 'MATH Short Answer: The point (5, 6) is reflected across the y-axis and the resulting point is then '
                'translated 4 units down. What are the coordinates of the final image point?',
           'a': ''},
          {'q': 'MATH Short Answer: At what x-value does the maximum value of the function f of x = 2x3 – 3x2 – 12x – '
                '6 occur on the closed interval from –4 to 4?',
           'a': '4'},
          {'q': 'MATH Short Answer: Given f inverse of x equals 2 – x, what is f(x)?', 'a': '2 – x'},
          {'q': 'MATH Short Answer: A triangle with integer side lengths has longest side that is 4 times as long as a '
                'second side, and the third side has length 20. What is the greatest possible perimeter of the '
                'triangle?',
           'a': '50'},
          {'q': 'MATH Short Answer: Consider a bag of 7 marbles, 5 red and 2 white. You draw marbles from the bag '
                'until you draw the last white marble, at which point you stop. What is the probability you stop '
                'drawing after the second marble is selected?',
           'a': '1/21'},
          {'q': 'MATH Short Answer: For the arithmetic sequence with first term 7 and fourth term 19, what is the sum '
                'of the first\n'
                '50 terms?',
           'a': '5250'},
          {'q': 'MATH Short Answer: What is the absolute value of the complex conjugate of –4 + 5i?', 'a': '√41'},
          {'q': 'MATH Short Answer: What is the limit as x approaches 3 of the fraction with numerator x6 – 81 and '
                'denominator x3 – 9?',
           'a': '36'},
          {'q': 'MATH Short Answer: An octagon is dilated with scale factor 7/4. What is the ratio of the areas of the '
                'original octagon to the image?',
           'a': '16/49'},
          {'q': 'MATH Short Answer: Other than 2, what is the smallest positive integer that, when divided by 3, 5, 7, '
                'or 9, has a remainder of 2?',
           'a': '317'},
          {'q': 'MATH Short Answer: If 6 dice are rolled and the numbers on the top faces are added together, how many '
                'different sums are possible?',
           'a': '31'},
          {'q': 'MATH Short Answer: What is the largest prime factor of the quantity\n42014 + 42015 + 42016 + 42017?',
           'a': '17'},
          {'q': 'MATH Short Answer: In the integers mod 12, what is 5 times 8?', 'a': '4'},
          {'q': 'MATH Short Answer: f of x is a twice differentiable function such that f prime of x and f double '
                'prime of x are both less than 0 for all real numbers. If f of 3 equals 12 and f of 5 equals 8, what '
                'is the largest possible integer value for f of 7?',
           'a': '3'},
          {'q': 'MATH Short Answer: What is the volume of a circular cylinder formed by rotating a 5 by 6 rectangular '
                'region about one of its shorter sides?',
           'a': '180π'},
          {'q': 'MATH Short Answer: The sums of three whole numbers taken in pairs are 11, 13, and 14. What is the '
                'product of these three numbers?',
           'a': '240'},
          {'q': 'MATH Short Answer: If exactly 10 diagonals of a particular convex polygon contain the same vertex, '
                'how many total sides does the polygon have?',
           'a': '13'},
          {'q': 'MATH Short Answer: In a particular year, if April 15 is on a Wednesday, on what day of the week is '
                'December 25?',
           'a': 'FRIDAY'},
          {'q': 'MATH Short Answer: What is the distance from the point (1, 3, 5) to the origin?', 'a': '√35'},
          {'q': 'MATH Short Answer: Consider an infinite geometric series with sum equal to 8/3 and first term 7/5. '
                'What is the value of the common ratio r for this series?',
           'a': '19/40'},
          {'q': 'MATH Short Answer: In a triple-elimination tournament, each game is played by two teams, there are no '
                'ties, and teams are eliminated when they have lost 3 times. What is the maximum number of games '
                'played if 83 teams enter?',
           'a': '248'},
          {'q': 'MATH Short Answer: What is the remainder when x6 + 3x4 – 2x3 + 7x – 3 is divided by x + 2?',
           'a': '111'},
          {'q': 'MATH Short Answer: The line with equation y = –2x + 5 is reflected across the y-axis. What is the '
                'slope-intercept equation of its image?',
           'a': 'y = 2x + 5'},
          {'q': 'MATH Short Answer: Triangle ABC has all angles with integral degree measures and the measure of angle '
                'A equals\n'
                '5 times the measure of angle B. How many possible degree measures are there for angle C?',
           'a': '29'},
          {'q': 'MATH Short Answer: Using the point names A, B, C, D, and E, how many different names are there for '
                'pentagon\n'
                'ABCDE?',
           'a': '10'},
          {'q': 'MATH Short Answer: What is the greatest common divisor of 234 and 2826?', 'a': '18'},
          {'q': 'MATH Short Answer: Consider a triangle with two sides with lengths of 4 and 9. How many different '
                'integers could be the length of the third side?',
           'a': '7'},
          {'q': 'MATH Short Answer: What is the limit as x approaches 0 of the fraction with numerator x – 1 + e to '
                'the power 3x and denominator sine x?',
           'a': '4'},
          {'q': 'MATH Short Answer: Evaluate the following expression: –i 33.', 'a': '–i'},
          {'q': 'MATH Short Answer: A triangular right prism has each edge of length 4. What is its surface area?',
           'a': '48 + 8√3'},
          {'q': 'MATH Short Answer: A set of test scores is normally distributed with mean 72 and standard deviation '
                '6. What score corresponds to a Z-score of –1.5?',
           'a': '63'},
          {'q': 'MATH Short Answer: A 5-digit palindrome has 3 different digits and is divisible by 18. What is its '
                'largest possible value?',
           'a': '89,298'},
          {'q': 'MATH Short Answer: What base-10 numeral does the following Roman numeral represent: CMXLVI?',
           'a': '946'},
          {'q': 'MATH Short Answer: What is the following cross product of vectors: 5i – 3j + k cross 4j?',
           'a': '–4i + 20k'}],
 'ess': [{'q': 'EARTH AND SPACE Multiple Choice: What layer of the Earth’s atmosphere contains approximately 75% of '
               'its air mass?\n'
               'W) Troposphere\n'
               'X) Mesosphere\n'
               'Y) Stratosphere\n'
               'Z) Thermosphere',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are true of seismic '
               'waves: 1) P waves are compressional; 2) S waves travel through fluids; 3) P waves travel faster than S '
               'waves.',
          'a': '1 AND 3'},
         {'q': 'EARTH AND SPACE Multiple Choice: What is the boundary that traps moisture and the associated weather '
               'in the troposphere?\n'
               'W) Mesosphere\n'
               'X) Mesoboundary\n'
               'Y) Tropopause\n'
               'Z) Stratopause',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: What state of matter is the most common in the universe?', 'a': 'PLASMA'},
         {'q': 'EARTH AND SPACE Multiple Choice: The Jurassic period occurred during which era?\n'
               'W) Cenozoic\n'
               'X) Mesozoic\n'
               'Y) Paleozoic\n'
               'Z) Neoproterozoic',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Christmas Pie is a small hamlet in Surrey, England, at\n'
               '51.25 degrees north latitude. In degrees to the nearest integer, what is the noon sun angle over\n'
               'Christmas Pie on the winter solstice?',
          'a': '15'},
         {'q': 'EARTH AND SPACE Multiple Choice: Hydraulic fracturing is used to obtain which of the following '
               'resources?\n'
               'W) Coal\n'
               'X) Natural gas\n'
               'Y) Uranium ore\n'
               'Z) Water',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Every silicate mineral contains what two elements?',
          'a': 'SILICON AND OXYGEN'},
         {'q': 'EARTH AND SPACE Multiple Choice: What gas accounts for approximately 78% of the dry volume of Earth’s '
               'atmosphere?\n'
               'W) Oxygen\n'
               'X) Nitrogen\n'
               'Y) Argon\n'
               'Z) Carbon dioxide',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: COROT [KOH-roh]was a mission run by the European\n'
               'Space Agency to find what type of celestial objects?',
          'a': 'EXOPLANETS'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of geologic fault is characterized by upward displacement '
               'of a footwall?\n'
               'W) Normal\n'
               'X) Reverse\n'
               'Y) Strike-slip\n'
               'Z) Thrust',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three characteristics that can be used to '
               'distinguish the mineral calcite from the mineral quartz: 1) Color; 2) Hardness;\n'
               '3) Birefringence [bye-ree-FRIN-jents].',
          'a': '2 AND 3'},
         {'q': 'EARTH AND SPACE Multiple Choice: Bauxite, the hydroxide ore of aluminum, is mined primarily from '
               'deposits in tropical areas. What process causes these deposits to form?\n'
               'W) Chemical weathering\n'
               'X) Magmatic intrusion\n'
               'Y) Lake turnover\n'
               'Z) Metasomatism',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: The Oso landslide that occurred in Washington State in\n'
               '2014 moved 1.2 kilometers across the North Fork Stillaguamish [STILL-ah-GWAH-mush]\n'
               'River in a single minute. What was the speed of this landslide in miles per hour, rounded to the '
               'nearest tenth?',
          'a': '44.7'},
         {'q': 'EARTH AND SPACE Short Answer: What subsurface phenomenon, defined as soil that is perennially frozen, '
               'occurs beneath much of the state of Alaska and, as it melts, causes extensive damage of roads, trains, '
               'and pipelines?',
          'a': 'PERMAFROST'},
         {'q': 'EARTH AND SPACE Short Answer: In the distant future, the Andromeda Galaxy will collide with the Milky '
               'Way. Which of the following would a hypothetical alien presently living in Andromeda observe about '
               'Balmer lines from our galaxy?\n'
               'W) Their wavelengths are shorter than expected\n'
               'X) Their wavelengths are longer than expected\n'
               'Y) Their frequencies are lower than expected\n'
               'Z) They are not subject to Zeeman splitting',
          'a': 'W) THEIR WAVELENGTHS ARE SHORTER THAN EXPECTED'},
         {'q': 'EARTH AND SPACE Short Answer: What geologic eon extends from around 542 million years ago through the '
               'present day?',
          'a': 'PHANEROZOIC'},
         {'q': 'EARTH AND SPACE Multiple Choice: Global warming leads to positive feedbacks that accelerate the '
               'greenhouse effect. Which of the following is an example of this?\n'
               'W) Plants photosynthesize more efficiently in a CO -rich atmosphere\n'
               'X) Reduced snow cover allows more solar radiation to warm the ground\n'
               'Y) More CO is sequestered by rock weathering in a warmer atmosphere\n'
               'Z) A warmer Earth loses more radiation to space',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: What mass movement of ocean water is referred to as the ocean conveyer '
               'belt?',
          'a': 'THERMOHALINE CIRCULATION'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are true of the '
               'Eagle Nebula: 1) It is an emission nebula; 2) It has a diameter of about 1 million light years; 3)\n'
               'It is part of the Kuiper belt.',
          'a': '1'},
         {'q': 'EARTH AND SPACE Short Answer: Crater Lake in Oregon occupies what type of volcanic feature?',
          'a': 'CALDERA'},
         {'q': "EARTH AND SPACE Multiple Choice: NASA's QuickSCAT satellite mapped winds over all of\n"
               "Earth's oceans. Which of the following is NOT true of this satellite?\n"
               'W) It bounced microwaves off the ocean surface\n'
               'X) It retrieved both wind direction and speed\n'
               'Y) Its orbit was geosynchronous\n'
               'Z) It was powered by solar arrays',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is a sedimentary rock?\n'
               'W) Scoria\n'
               'X) Granite\n'
               'Y) Basalt\n'
               'Z) Shale',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three processes that remove nitrogen gas '
               "from Earth's atmosphere: 1) Nitrogen fixation; 2) Denitrification; 3) Forest fires.",
          'a': '1 ONLY'},
         {'q': 'EARTH AND SPACE Short Answer: What band of tall clouds and thunderstorms, also known among sailors as '
               'the doldrums, occurs at low latitudes between the Northern and Southern hemisphere trade winds?',
          'a': 'INTERTROPICAL CONVERGENCE ZONE'},
         {'q': 'EARTH AND SPACE Multiple Choice: Jupiter appears brightest in which of the following configurations '
               'relative to the Earth?\n'
               'W) Conjunction\n'
               'X) Quasi conjunction [KWAH-zye kon-JUNK-shun]\n'
               'Y) Quadrature\n'
               'Z) Opposition',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following geologic eons lasted the longest?\n'
               'W) Hadean\n'
               'X) Archean [ar-KEE-en]\n'
               'Y) Proterozoic [proh-tair-oh-ZOH-ik]\n'
               'Z) Phanerozoic [fah-NAIR-oh-zoh-ik]',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three factors that threaten\n'
               'California’s water supplies: 1) Slow reservoir recharge rates; 2) High agricultural water consumption; '
               '3) Strike-slip faults intersecting major aqueducts.',
          'a': 'ALL OF THEM'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following best describes the relationship between the '
               'ages of the Earth, the Sun, and the Universe?\n'
               'W) The Universe is about 3 times as old as the Sun, which is about 3 times as old as the Earth\n'
               'X) The Universe is the same age as the Sun, which is about 3 times as old as the Earth\n'
               'Y) The Universe is about 3 times as old as the Sun and the Earth, which are the same age\n'
               'Z) The Universe, the Earth, and the Sun are all the same age',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: You are in a Northern Hemisphere region experiencing zonal air flow with '
               'a low pressure system to your north. Which direction would you need to face if you wanted to place '
               'your back to the oncoming wind?',
          'a': 'EAST'},
         {'q': 'EARTH AND SPACE Short Answer: What is the nearest galaxy cluster?', 'a': 'VIRGO'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is most directly associated with\n'
               'Andean-type plate margins?\n'
               'W) Volcanic arcs\n'
               'X) Extensional faulting\n'
               'Y) Rift valleys\n'
               'Z) Hot spot activity',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following phenomena is a buildup of ocean water that is '
               'pushed towards land by a hurricane?\n'
               'W) Tsunami\n'
               'X) Surge tide\n'
               'Y) Storm surge\n'
               'Z) Rogue wave',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: What element is the second most abundant in the\n'
               'Earth’s crust, but is NOT commonly found on Earth in its elemental form?',
          'a': 'SILICON'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following planets has rings?\n'
               'W) Mars\n'
               'X) Mercury\n'
               'Y) Neptune\n'
               'Z) Venus',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Put the following four minerals in order from softest to hardest on the '
               'Mohs scale: 1) Apatite; 2) Fluorite; 3) Quartz; 4) Corundum.',
          'a': '2, 1, 3, 4'},
         {'q': "EARTH AND SPACE Short Answer: What volcano hosts the world's primary benchmark site for atmospheric "
               'carbon dioxide measurements and the observatory that produced the original Keeling curve?',
          'a': 'MAUNA LOA'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following best explains how and why galaxies in the '
               'universe are moving relative to each other?\n'
               'W) Most galaxies are moving away from each other because space is expanding\n'
               'X) All galaxies are moving toward each other because space is contracting\n'
               'Y) Most galaxies are moving away from each other because space is contracting\n'
               'Z) All galaxies are moving toward each other because space is expanding',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: If a slow-moving warm front is followed by a fast- moving cold front, '
               'the cold front will sometimes overtake the warm front. When the cold air lifts the warm air entirely '
               'aloft, what atmospheric phenomenon results?\n'
               'W) Stationary front\n'
               'X) Occluded front\n'
               'Y) Marine front\n'
               'Z) Polar front',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three constellations and asterisms that '
               'would be visible in the December night sky over the North Pole: 1) Cassiopeia; 2)\n'
               'Crux; 3) The Big Dipper.',
          'a': '1 AND 3'},
         {'q': 'EARTH AND SPACE Short Answer: At what type of plate boundary is there no destruction or creation of '
               'lithosphere due to the relative motion being in the horizontal direction?',
          'a': 'TRANSFORM'},
         {'q': 'EARTH AND SPACE Short Answer: A stream is referred to as a “gaining stream” when its surface is below '
               'what groundwater feature?',
          'a': 'WATER TABLE'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following elements most often limits primary production '
               'in freshwater lakes?\n'
               'W) Oxygen\n'
               'X) Calcium\n'
               'Y) Carbon\n'
               'Z) Phosphorus',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are true of wooly '
               'mammoths: 1) They once lived in North America; 2) They had ivory tusks; 3) They evolved in the '
               'Devonian Period.',
          'a': '1 AND 2'},
         {'q': 'EARTH AND SPACE Short Answer: When subjected to intense heat and pressure, limestone becomes which '
               'non-foliated metamorphic rock?',
          'a': 'MARBLE'},
         {'q': 'EARTH AND SPACE Multiple Choice: Addition of which of the following compounds may promote carbon '
               'sequestration in the ocean?\n'
               'W) Potassium hydroxide\n'
               'X) Carbonic acid\n'
               'Y) Hydrochloric acid\n'
               'Z) Sulfur',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: The Montreal Protocols were a series of international agreements to '
               'phase out what harmful pollutants that destroy stratospheric ozone?',
          'a': 'CHLOROFLUOROCARBONS'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is NOT true of tropical forest soils in '
               'relation to temperate forest soils?\n'
               'W) Tropical forest soils are richer in nutrients\n'
               'X) Tropical forest soils experience more intense leaching\n'
               'Y) Temperate forest soils retain more organic matter\n'
               'Z) Temperate forest soils are thicker',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: In what constellation is our Galactic center located?',
          'a': 'SAGITTARIUS'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following best describes the composition of\n'
               'Earth’s core?\n'
               'W) 78% silicon oxide\n'
               'X) Mainly iron silicates\n'
               'Y) An iron-nickel alloy\n'
               'Z) Mainly iron and potassium compounds',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: The majority of Earth’s freshwater is found in which of the '
               'following?\n'
               'W) The Pacific Ocean\n'
               'X) Ice and snow\n'
               'Y) Subsurface streams\n'
               'Z) The atmosphere as water vapor',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Classify the following three volcanoes according to whether they formed '
               'at convergent plate boundaries, divergent plate boundaries, or hot spots, respectively:\n'
               '1) Yellowstone; 2) Kilauea; 3) Mount Etna.',
          'a': '1 – HOT SPOT; 2 – HOT SPOT; 3 - CONVERGENT'},
         {'q': 'EARTH AND SPACE Short Answer: The precession of the equinoxes is due principally to the torque induced '
               'on the Earth by what celestial body?',
          'a': 'THE MOON'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three marine regions that host coral '
               'reefs: 1) The Red Sea; 2) The Australian Coast; 3) The Brazilian Coast.',
          'a': 'ALL OF THEM'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following cloud types is strongly associated with '
               'thunderstorms?\n'
               'W) Cirrocumulus [seer-oh-KYOOM-you-lus]\n'
               'X) Cumulonimbus [KYOOM-yoo-loh-NIM-bus]\n'
               'Y) Altostratus\n'
               'Z) Stratocumulus',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: The Hubble Deep Field is an image of a seemingly empty spot in the sky '
               'in what constellation?',
          'a': 'URSA MAJOR'},
         {'q': 'EARTH AND SPACE Short Answer: What features on the Sun, caused by strong magnetic fields, vary in '
               'number with an 11 year cycle?',
          'a': 'SUNSPOTS'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following coasts parallels a nearby tectonic plate '
               'boundary?\n'
               'W) East Coast of North America\n'
               'X) West Coast of Australia\n'
               'Y) West Coast of South America\n'
               'Z) West Coast of Africa',
          'a': 'Y'},
         {'q': "EARTH AND SPACE Multiple Choice: Which of the following gases is most likely to escape from a planet's "
               'atmosphere?\n'
               'W) Hydrogen\n'
               'X) Helium\n'
               'Y) Methane\n'
               'Z) Ammonia',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What geologic era began following the Cretaceous-\n'
               'Paleogene [PAY-leo-jeen] extinction?',
          'a': 'CENOZOIC'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three conditions that can cause '
               'metamorphism of rocks: 1) High temperature; 2) High acidity; 3) High pressure.',
          'a': '1, 3'},
         {'q': 'EARTH AND SPACE Multiple Choice: The United States has the highest frequency of tornado occurrences of '
               "the world's nations. To the nearest order of magnitude, how many tornadoes touch down in the United "
               'States each year?\n'
               'W) One hundred\n'
               'X) One thousand\n'
               'Y) Ten thousand\n'
               'Z) One hundred thousand',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is the mechanism by which strain energy is '
               'released during earthquakes?\n'
               'W) Elastic rebound\n'
               'X) Solution-collapse\n'
               'Y) Hydrostatic pressure\n'
               'Z) Volcanic degassing',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is a NOT a way in which scientists test the '
               'reliability of computer models of future climate?\n'
               'W) Comparing model predictions of recent past climate to observed records\n'
               'X) Comparing model predictions of distant past climate to proxy records\n'
               'Y) Checking for consistency between the outputs of many differently constructed models\n'
               'Z) Confirming that models have accurately predicted local weather events each year',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following minerals is a crystalline form of silicon '
               'dioxide?\n'
               'W) Mica\n'
               'X) Quartz\n'
               'Y) Calcite\n'
               'Z) Feldspar',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Order the following four color classifications of stars from least to '
               'greatest surface temperatures: 1) Yellow; 2) Blue; 3) Red; 4) White.',
          'a': '3, 1, 4, 2'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following minerals has only one plane of cleavage?\n'
               'W) Hornblende\n'
               'X) Biotite\n'
               'Y) Potassium feldspar\n'
               'Z) Augite [AW-jite]',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are true of the '
               'contrails produced by air traffic: 1) They are mostly composed of water ice; 2) They have a high '
               'albedo relative to oceans and forests; 3) They form in unstable, convecting layers of the atmosphere.',
          'a': '1 AND 2'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is a fine-grained, typically buff- colored '
               'sediment deposited by wind?\n'
               'W) Evaporite\n'
               'X) Loess [LOH-ess]\n'
               'Y) Glaze\n'
               'Z) Humus [HYOO-muss]',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: What is the discharge, in meters cubed per second, of a simple river '
               'that is 5 meters deep, 10 meters wide, and has a current speed of 5 meters per second?',
          'a': '250'},
         {'q': "EARTH AND SPACE Short Answer: What country has emitted the most carbon dioxide to Earth's atmosphere "
               'during the past five years?',
          'a': 'CHINA'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is NOT characteristic of currents found on the '
               'western boundary of oceanic gyres, relative to other ocean currents?\n'
               'W) Warm\n'
               'X) Deep\n'
               'Y) Narrow\n'
               'Z) Slow-moving',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following laws expresses the increase in redshift of a '
               "galaxy's spectral lines with distance?\n"
               'W) Doppler’s Law\n'
               'X) Cepheid’s Law\n'
               'Y) Hubble’s Law\n'
               'Z) Kepler’s Law',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are true regarding '
               'the differences between S waves and P waves: 1) P waves are longitudinal waves, while S waves are '
               'transverse waves; 2) P waves tend to have much larger amplitudes than S waves; 3) P waves travel '
               'faster than S waves.',
          'a': '1 AND 3'},
         {'q': 'EARTH AND SPACE Short Answer: What is the term for a Kuiper [KYE-pur] belt object that has been '
               'scattered into the region of the outer planetary orbits?',
          'a': 'CENTAUR'},
         {'q': 'EARTH AND SPACE Short Answer: Two stars have the same absolute magnitude. One is at a distance of 10 '
               'parsecs and the other is at a distance of 100 parsecs. What is the positive difference in their '
               'apparent magnitudes?',
          'a': '5'},
         {'q': 'EARTH AND SPACE Multiple Choice: How does the synodic period of the moon relate to its sidereal '
               'period?\n'
               'W) Its synodic period is two days longer\n'
               'X) Its synodic period is one day shorter\n'
               'Y) Its synodic period is one day longer\n'
               'Z) Its synodic period is two days shorter',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: The spectra of type IA supernovae are unique because they do NOT contain '
               'lines for what element?',
          'a': 'HYDROGEN'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following conditions is common to both warm and cold '
               'fronts?\n'
               'W) Steady barometer readings\n'
               'X) Divergence of surface winds\n'
               'Y) Decreasing precipitation rates\n'
               'Z) Lifting of warm air over a cold air mass',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is a reason that long-term preservation of '
               'deep sea carbonates is rare?\n'
               'W) Most ocean crust and overlying sediments are subducted\n'
               'X) Most parts of the deep ocean floor lie above the carbonate compensation depth\n'
               'Y) There is little carbonate-forming material occurring in ocean water\n'
               'Z) Carbonates react with silicates in the deep ocean',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is true about radiometric dating?\n'
               'W) All parent material in a mineral is converted to the daughter product\n'
               'X) When the quantities of parent and daughter products are equal, two half-lives have transpired\n'
               'Y) The number of radioactive atoms that decay during one half life is always the same\n'
               'Z) The percentage of radioactive atoms that decay during one half life is always the same',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following statements that are true about zodiacal '
               'light: 1) It is produced when sunlight is scattered by cosmic dust; 2) It appears as a faint white '
               'glow near the horizon; 3) It is best viewed at midnight.',
          'a': '1 AND 2'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following countries has lost the greatest land area of '
               'forest to deforestation over the past decade?\n'
               'W) Brazil\n'
               'X) Ecuador\n'
               'Y) Zimbabwe\n'
               'Z) Venezuela',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: Arrange the following distances in our Solar System from smallest to '
               'largest, taking thickness to mean the difference between the outer and inner radii of an annulus or '
               'spherical shell: 1) Thickness of the Oort cloud; 2) Separation of Earth and Venus at inferior '
               'conjunction; 3) Thickness of the asteroid belt.',
          'a': '2, 3, 1'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following low pressure systems typically has the weakest '
               'sustained wind speed?\n'
               'W) Tropical storm\n'
               'X) Tropical depression\n'
               'Y) Hurricane\n'
               'Z) Tropical wave',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: What is the period in years of two stars, each with a mass of two solar '
               'masses, in an orbit with a semi-major axis of 1600 AU and an eccentricity of 0.5?',
          'a': '32000'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is NOT an example of an ichnofossil?\n'
               'W) Shell\n'
               'X) Burrow\n'
               'Y) Coprolite\n'
               'Z) Urolite',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: In what month does light take longest to travel from the Sun to the '
               'Earth?',
          'a': 'JULY'},
         {'q': 'EARTH AND SPACE Short Answer: From what common halide mineral is hydrofluoric acid manufactured?',
          'a': 'FLUORITE'},
         {'q': 'EARTH AND SPACE Short Answer: What formation of porous sand and gravel, covering\n'
               '450,000 square kilometers just east of the Rocky Mountains, is the largest aquifer in the United\n'
               'States?',
          'a': 'OGALLALA FORMATION'},
         {'q': 'EARTH AND SPACE Short Answer: What is the plutonic equivalent of andesite?', 'a': 'DIORITE'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following four objects around which accretion disks '
               'are sometimes present: 1) White dwarfs; 2) Protostars; 3) Stellar mass black holes;\n'
               '4) Supermassive black holes.',
          'a': 'ALL OF THEM'},
         {'q': 'EARTH AND SPACE Multiple Choice: Why was the 2010 Haiti earthquake registered so high on the Mercalli '
               'Intensity Scale despite smaller ratings on the Richter and Moment Magnitude scales?\n'
               'W) The earthquake produced a large tsunami\n'
               'X) The initial earthquake was followed by many aftershocks\n'
               'Y) Haiti is underlain by thrust faults\n'
               'Z) Haiti has a poorly developed infrastructure',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: Phosphorus is an essential nutrient for phytoplankton.\n'
               'Identify all of the following three processes that remove phosphorus from the Indian Ocean photic '
               'zone: 1) Marine snow; 2) Coastal upwelling; 3) Deposition of windblown dust from Australia.',
          'a': '1'},
         {'q': 'EARTH AND SPACE Short Answer: What fast-flowing, narrow currents form above sharp air mass boundaries '
               'in the atmospheres of rotating planets, including Earth?',
          'a': 'JET STREAMS'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following main-sequence stars are the least massive?\n'
               'W) Blue\n'
               'X) Red\n'
               'Y) Yellow\n'
               'Z) White',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is NOT true of the lunar maria?\n'
               "W) They formed within the first one billion years of the moon's history\n"
               "X) They cover about 50% of the moon's surface\n"
               'Y) They are composed of iron-rich basalt\n'
               'Z) They are more abundant on the near side of the moon',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Order the following three groups of photosynthetic organisms by their '
               'time of appearance on Earth, from first to last: 1) Cyanobacteria [sye-ANNO- bacteria]; 2) C4 plants; '
               '3) Ferns.',
          'a': '1, 3, 2'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following metamorphic rocks cannot originate from '
               'shale?\n'
               'W) Anthracite\n'
               'X) Gneiss [nice]\n'
               'Y) Slate\n'
               'Z) Phyllite [FILL-lite]',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: Approximately how many meters would global average sea level rise if '
               'both the Greenland and Antarctic ice sheets were to completely melt?\n'
               'W) 10\n'
               'X) 30\n'
               'Y) 70\n'
               'Z) 120',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is always true during the month of\n'
               'July?\n'
               'W) The Earth is near its orbital perihelion\n'
               'X) The Southern Hemisphere is tilted towards the Sun\n'
               'Y) The sun does not rise over the Drake Passage\n'
               'Z) The sun does not set over Svalbard',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: What is the resolving power, in arc seconds to one decimal place, of a '
               '56.0 centimeter diffraction-limited telescope observing in the V band?',
          'a': '0.2'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following sedimentary rocks has a clastic composition?\n'
               'W) Dolostone\n'
               'X) Limestone\n'
               'Y) Shale\n'
               'Z) Coal',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are TRUE regarding '
               'calderas: 1) Calderas can form atop shield volcanoes; 2) Basalt-filled calderas tend to result from '
               'explosive eruptions; 3) Calderas can be found on Venus and Io.',
          'a': '1 AND 3'},
         {'q': 'EARTH AND SPACE Short Answer: What region of the H-R diagram, named after a Japanese astrophysicist, '
               'is occupied by protostars of fewer than 3 solar masses?',
          'a': 'HAYASHI TRACK'},
         {'q': 'EARTH AND SPACE Short Answer: A given mineral sample consists of pale yellow rhombohedral crystals '
               'that scratch gypsum. A laser beam directed through the sample splits in two, and a drop of '
               'hydrochloric acid placed on the sample effervesces vigorously. What is the chemical formula of the '
               'mineral?',
          'a': 'CaCO'},
         {'q': 'EARTH AND SPACE Multiple Choice: If the ambient air cools 8 degrees Celsius for each kilometer of '
               'vertical elevation you gain as you ascend a low mountain in Tennessee, which of the following most '
               'likely describes the stability of the local atmosphere?\n'
               'W) Absolutely unstable\n'
               'X) Conditionally unstable\n'
               'Y) Neutrally stable\n'
               'Z) Absolutely stable',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Order the following four planets from least dense to most dense: 1) '
               'Mercury; 2) Mars; 3) Jupiter; 4) Saturn.',
          'a': '4, 3, 2, 1'},
         {'q': 'EARTH AND SPACE Short Answer: What class of barred spiral galaxies has the most tightly wound arms?',
          'a': 'SBa'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following rock types would be most susceptible to '
               'chemical weathering by tropical rainfall?\n'
               'W) Granite\n'
               'X) Andesite\n'
               'Y) Dacite\n'
               'Z) Basalt',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following clay minerals forms from the weathering of '
               'feldspar and is the main component of most porcelain?\n'
               'W) Kaolinite\n'
               'X) Chlorite\n'
               'Y) Saponite\n'
               'Z) Vermiculite',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What is the right ascension, to the nearest hour, of the Sun on the '
               'summer solstice?',
          'a': '6'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following gases varies the most by volume within the '
               'planetary boundary layer?\n'
               'W) Ozone\n'
               'X) Oxygen\n'
               'Y) Water vapor\n'
               'Z) Carbon dioxide',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Given that the global average precipitation is 1000 millimeters per year '
               "and the total water vapor in the Earth's atmosphere is estimated to equal a liquid water layer of 25 "
               'millimeters, to the nearest whole number of days, what is the average residence time of water vapor in '
               "the earth's atmosphere?",
          'a': '9'},
         {'q': 'EARTH AND SPACE Multiple Choice: Striations, U-shaped valleys, and fjords are all landscape features '
               'formed by what process?\n'
               'W) Fluvial erosion\n'
               'X) Fluvial deposition\n'
               'Y) Glacial erosion\n'
               'Z) Glacial deposition',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Given that a day on Jupiter is about ten hours long, rank the following '
               'surface locations on the Earth and Jupiter from the one that experiences the smallest\n'
               "Coriolis effect to the one that experiences the greatest Coriolis effect: 1) Jupiter's equator; 2)\n"
               "Jupiter's North pole; 3) Earth's North pole; 4) Earth's tropic of Cancer.",
          'a': '1, 4, 3 2'},
         {'q': 'EARTH AND SPACE Multiple Choice: In a landlocked area with multiple playas and sparse low-lying '
               'vegetation, what type of research would best reveal how the local climate has changed over the past '
               'several thousand years?\n'
               'W) Palynology\n'
               'X) Sclerochronology [sklair-oh-kraw-NAW-lah-jee]\n'
               'Y) Dendroclimatology [den-droh-klye-mah-TALL-ah jee]\n'
               'Z) Speleology [speel-ee-AWL-ah-jee]',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: A fictional moon in a faraway galaxy has the same mass and atmospheric '
               'composition as the Earth, but its radius is twice as large. To one decimal place, in kelvins per '
               'kilometer, what would be the dry adiabatic lapse rate in this moon’s atmosphere?',
          'a': '2.5'},
         {'q': 'EARTH AND SPACE Multiple Choice: Saltwater desalination is a very energy-intensive process when '
               'practiced at large scale. What technology is predominantly used for saltwater desalination in the '
               'United States?\n'
               'W) Reverse osmosis\n'
               'X) Ion exchange\n'
               'Y) Salt precipitation\n'
               'Z) Solar distillation',
          'a': 'W'},
         {'q': "EARTH AND SPACE Short Answer: NASA's Aqua MODIS [MOH-diss] satellite instrument senses the color of "
               "Earth's surface oceans. Identify all of the following three statements relevant to Aqua MODIS data "
               'that are true: 1) The greenest seawater is found at the centers of ocean gyres; 2) A bloom of '
               'coccolithophores [caw-koh-LITH-oh-foorz] increases seawater albedo; 3)\n'
               'A bloom of cyanobacteria absorbs light in the 430-450 nanometer band.',
          'a': '2 AND 3'},
         {'q': "EARTH AND SPACE Multiple Choice: What bright features extending from the Sun's photosphere, often "
               'loop-shaped, are composed of relatively cool plasma that emits visible light?\n'
               'W) Sunspots\n'
               'X) Flares\n'
               'Y) Prominences\n'
               'Z) Van Allen belts',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Greenschists and blueschists both derive from mafic parent rocks. Why '
               'do they have different mineral compositions?\n'
               'W) They formed at different pressures and temperatures\n'
               'X) They crystallized at different rates\n'
               'Y) Greenschists are acidic\n'
               'Z) Blueschists were exposed to oxygen',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What type of rotating neutron stars are classified into '
               'rotation-powered, accretion-powered, and magnetars?',
          'a': 'PULSARS'},
         {'q': 'EARTH AND SPACE Multiple Choice: A breccia lens, shatter cones, tektites and spherulites can be found '
               'in which of the following areas?\n'
               'W) Cape Cod, Massachusetts\n'
               'X) Chesapeake Bay, Virginia\n'
               'Y) Honolulu, Hawaii\n'
               'Z) Yellowstone, Wyoming',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following statements is NOT true regarding the planet '
               'Mercury?\n'
               'W) Mercury is more massive than Ganymede\n'
               'X) Mercury has a magnetic field generated by a liquid iron core\n'
               'Y) Mercury is synchronously tidally locked with the Sun\n'
               "Z) Craters on Mercury's north pole are known to contain water ice",
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three quantities that have increased '
               'globally due to human activities: 1) Flux of sediment into the oceans from streams; 2)\n'
               'Area of rainforest in the tropics; 3) Total volume of groundwater in aquifers.',
          'a': '1'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three phenomena that are formed by aeolian '
               'processes: 1) Yardangs; 2) Ventifacts; 3) Dunes.',
          'a': 'ALL OF THEM'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three events that occurred during the '
               'recombination epoch of the Big Bang: 1) Formation of neutral hydrogen; 2) Neutrino decoupling; 3) Star '
               'formation.',
          'a': '1 ONLY'},
         {'q': 'EARTH AND SPACE Short Answer: What allotrope of carbon is known for its strong bonds within the plane, '
               'but weak bonds between planes?',
          'a': 'GRAPHITE'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following regions of an active galactic nucleus is the '
               'most distant from the supermassive black hole?\n'
               'W) Accretion disk\n'
               'X) Broad line region\n'
               'Y) Narrow line region\n'
               'Z) Obscuring torus',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Refracting telescopes have a severe limitation in that each wavelength '
               'of light is refracted differently, making it impossible to focus on more than one wavelength of light '
               'at a time. What is this type of optical aberration called?',
          'a': 'CHROMATIC ABERRATION'},
         {'q': 'EARTH AND SPACE Multiple Choice: A red breccia contains a high percentage of large angular feldspar '
               'grains. In what type of depositional environment would you expect it to have formed?\n'
               'W) Beach\n'
               'X) Alluvial fan\n'
               'Y) Deep ocean trench\n'
               'Z) River delta',
          'a': 'X'}, {'q': 'EARTH AND SPACE Multiple Choice: Which of the following earthquake waves travels the slowest?\n'
               'W) Body\n'
               'X) Primary\n'
               'Y) Secondary\n'
               'Z) Rayleigh',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: What is the largest shield volcano in our Solar System?',
          'a': 'OLYMPUS MONS'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of mineral composes the green sand beaches that are found '
               'in the state of Hawaii?\n'
               'W) Malachite\n'
               'X) Augite\n'
               'Y) Jade\n'
               'Z) Olivine',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: A star has a parallax of 0.4 arcseconds. To the nearest whole light '
               'year, how far away is the star?',
          'a': '8'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is NOT true regarding white dwarfs?\n'
               'W) They shrink in radius as they get cooler\n'
               'X) They do not perform nuclear fusion\n'
               'Y) Their mass is mostly composed of carbon and oxygen\n'
               'Z) They can have atmospheres of helium',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: The Herschels proposed a model of the Milky Way that suggested that '
               'our solar system was near the center. Which of the following did they not account for in their model?\n'
               "W) The Sun's brightness only enables us to see a limited distance into the Milky Way\n"
               'X) Their telescopes were not powerful enough to see the edge of the Milky Way\n'
               'Y) Interstellar dust obscures much of the Milky Way from our vantage point\n'
               'Z) Their sampling of stars was biased in one direction',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: What is the term, literally meaning “burning cloud”, for a glowing '
               'pyroclastic flow that can reach speeds of 200 kilometers per hour?',
          'a': 'NUEE ARDENTE'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of mass wasting event is created when many different '
               'sediment sizes channelize and begin to move in a fluidized mass down slope?\n'
               'W) Debris flow\n'
               'X) Rock avalanche\n'
               'Y) Earth flow\n'
               'Z) Debris slide',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of metamorphism occurs when magma is injected into crustal '
               'rock and the heat of the intrusion causes the crustal rock to metamorphose?\n'
               'W) Contact\n'
               'X) Regional\n'
               'Y) Burial\n'
               'Z) Hydrothermal',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: The volume of Lake Michigan is 5 times 10 to the 12 cubic meters. If the '
               'flow rate of water into Lake Michigan is 5 times 10 to the 10 cubic meters per year, how long, in '
               'years to one significant digit, is the residence time of water in lake Michigan?',
          'a': '100'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following minerals is not a carbonate?\n'
               'W) Rhodochrosite\n'
               'X) Fluorite\n'
               'Y) Azurite\n'
               'Z) Calcite',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: A star has five times the radius of the Sun, and the temperature in '
               'kelvins of its surface is twice that of the Sun. How many times as luminous as the Sun is it?',
          'a': '400'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following materials would make the best aquitard?\n'
               'W) Sand\n'
               'X) Limestone\n'
               'Y) Clay\n'
               'Z) Gravel',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following statements is NOT true regarding neutron '
               'stars?\n'
               'W) They are supported by electron degeneracy pressure\n'
               'X) Pulsars are thought to be a type of neutron star\n'
               'Y) After initial neutrino burn-off, neutron stars cool slowly due to their small surface area\n'
               'Z) The center of the Crab Nebula is a neutron star',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: Which of the four terrestrial planets is most unlike the others in '
               'density?',
          'a': 'MARS'},
         {'q': 'EARTH AND SPACE Multiple Choice: What phenomenon is believed to be the main driver in the accelerated '
               'expansion of the universe?\n'
               'W) Dark matter\n'
               'X) Black hole evaporation\n'
               'Y) Dark energy\n'
               'Z) Quantum gravity',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of earthquake wave is associated with ground roll?\n'
               'W) Love wave\n'
               'X) P-wave\n'
               'Y) Rayleigh wave\n'
               'Z) S-wave',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Galena is an ore of what element?', 'a': 'LEAD'},
         {'q': 'EARTH AND SPACE Multiple Choice: What is found in clouds that can acquire opposite charges, creating '
               'the potential for lightning?\n'
               'W) Entrained mist\n'
               'X) Liquid water\n'
               'Y) Dust grains\n'
               'Z) Ice crystals',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: With what type of plate boundary is the Mariana Trench associated?',
          'a': 'CONVERGENT'},
         {'q': 'EARTH AND SPACE Multiple Choice: In what cloud type does hail generally form?\n'
               'W) Cirrocumulus\n'
               'X) Cirrostratus\n'
               'Y) Altocumulus\n'
               'Z) Cumulonimbus',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: You find a chunk of granite that you conclude, via radiometric '
               'dating, is 3.2 billion years old. The granite also contains inclusions of quartzite. Which of the '
               'following is a reasonable conclusion based on this data?\n'
               'W) The quartzite likely formed less than 3.2 billion years ago\n'
               'X) Because the quartzite is contained in the granite, it also formed 3.2 billion years ago\n'
               'Y) The quartzite likely formed more than 3.2 billion years ago\n'
               'Z) The sandstone from which the quartzite came is likely older than 3.2 billion years, but the '
               'quartzite itself is younger than that',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: What causes the trees in Alaskan forests to start tilting in many '
               'different directions, creating an area called a drunken forest?',
          'a': 'THAWING SOIL'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of faulting is defined by strike-slip offset along an '
               'essentially vertical fault plane?\n'
               'W) Normal\n'
               'X) Reverse\n'
               'Y) Thrust\n'
               'Z) Transcurrent',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of fault created the Loma Prieta earthquake in 1989?\n'
               'W) Normal\n'
               'X) Reverse\n'
               'Y) Strike-slip\n'
               'Z) Thrust',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: What is the parent rock of slate?', 'a': 'SHALE'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of rock is found in most cave systems?\n'
               'W) Sandstone\n'
               'X) Granite\n'
               'Y) Basalt\n'
               'Z) Limestone',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: According to the Richter scale, to the nearest whole number, how many '
               'times as much energy does a 5.7 earthquake release as a 4.7 earthquake?',
          'a': '32'},
         {'q': 'EARTH AND SPACE Multiple Choice: What is the name for a stream that is similar to a braided stream but '
               'the mid- channel bars are much more stable than those found in a braided stream?\n'
               'W) Meandering\n'
               'X) Wandering\n'
               'Y) Anastomosing\n'
               'Z) Sinuous',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following types of olivine has the highest iron '
               'content?\n'
               'W) Forsterite\n'
               'X) Fayalite\n'
               'Y) Monticellite\n'
               'Z) Tephroite',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: What is the general term for the data-gathering technique by which the '
               'measurements of several smaller telescopes are superimposed to create a higher-resolution and more '
               'detailed image?',
          'a': 'INTERFEROMETRY'},
         {'q': 'EARTH AND SPACE Short Answer: Fossils of Mesosaurus were instrumental in providing evidence for what '
               'theory?',
          'a': 'CONTINENTAL DRIFT'},
         {'q': 'EARTH AND SPACE Multiple Choice: What is the term for a fluidized mixture of solid to semi-solid '
               'fragments and hot expanding gases that flows under gravity down the flanks of a volcano during an '
               'eruption?\n'
               'W) Pyroclastic surge\n'
               'X) Lahar\n'
               'Y) Pyroclastic flow\n'
               'Z) Lava flow',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three locations where continental ice '
               'sheets can be currently found: 1) Greenland; 2) North America; 3) Antarctica.',
          'a': '1 AND 3'},
         {'q': 'EARTH AND SPACE Multiple Choice: The La Brea Tar Pits of Los Angeles, California, are famous for the '
               'quantity and diversity of fossils of extinct Pleistocene animals. Which of the following is closest to '
               'the number of years ago that these pits formed?\n'
               'W) 40,000\n'
               'X) 400,000\n'
               'Y) 4,000,000\n'
               'Z) 40,000,000',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are true regarding '
               'the waves produced by earthquakes: 1) S waves are transverse waves; 2) S waves only travel through '
               'solids; 3) S waves travel faster than P waves.',
          'a': '1 AND 2'},
         {'q': 'EARTH AND SPACE Multiple Choice: Greenhouse gases build up in the atmosphere of Earth and limit the '
               'amount of heat escaping back into space. Which of the following is not a greenhouse gas for Earth?\n'
               'W) Carbon dioxide\n'
               'X) Argon\n'
               'Y) Nitrous oxide\n'
               'Z) Methane',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Multiple Choice: What coordinate is the celestial-sphere equivalent of latitude?\n'
               'W) Declination\n'
               'X) Right-ascension\n'
               'Y) Altitude\n'
               'Z) Zenith angle',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What type of tide is caused when the gravitational forces of the Sun and '
               'Moon coincide?',
          'a': 'SPRING TIDES'},
         {'q': "EARTH AND SPACE Short Answer: Pahoehoe and a'a are lava flows associated with what type of magma?",
          'a': 'BASALTIC'},
         {'q': 'EARTH AND SPACE Multiple Choice: The earliest known single-celled life forms on Earth belong to which '
               'of the following taxonomic groups?\n'
               'W) Fungi\n'
               'X) Protoctista\n'
               'Y) Plantae\n'
               'Z) Monera',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: What is the chief commercial ore of aluminum?', 'a': 'BAUXITE'},
         {'q': 'EARTH AND SPACE Short Answer: Most long-period comets are thought to originate from what region in the '
               'solar system?',
          'a': 'OORT CLOUD'},
         {'q': 'EARTH AND SPACE Short Answer: In 1943, a volcano suddenly appeared in a corn field in the village of '
               'Paricutin and began erupting lava bombs and ash. What type of volcano was this?',
          'a': 'CINDER CONE'},
         {'q': 'EARTH AND SPACE Multiple Choice: We see the same side of the moon here on Earth all the time due to '
               'what effect?\n'
               'W) Lagrange point\n'
               'X) Gravitational lensing\n'
               'Y) Tidal locking\n'
               'Z) Asynchronous spin',
          'a': 'Y'},
         {'q': "EARTH AND SPACE Multiple Choice: What layer of the Earth's atmosphere varies in depth with the time of "
               'day and reflects radio waves long distances?\n'
               'W) Photosphere\n'
               'X) Stratosphere\n'
               'Y) Troposphere\n'
               'Z) Ionosphere',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: What is the second brightest star in the night sky?', 'a': 'CANOPUS'},
         {'q': 'EARTH AND SPACE Short Answer: What famous lake was formed as a result of the collapse of Mount Mazama?',
          'a': 'CRATER LAKE'},
         {'q': 'EARTH AND SPACE Short Answer: What term, combining the Greek words for blanket and rock, describes the '
               'loose, incoherent material of any origin on the surface of a planet or satellite?',
          'a': 'REGOLITH'},
         {'q': 'EARTH AND SPACE Multiple Choice: A barchan dune developes perpendicular to a moderate-velocity, '
               'uniform wind.\n'
               'Which of the following dunes is developed by variable wind direction?\n'
               'W) Star\n'
               'X) Longitudinal\n'
               'Y) Seif\n'
               'Z) Dome',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: After the first 4 billion years of Earth’s history, what relatively '
               'short evolutionary event brought forth most major animal phyla, as evidenced in the fossil record?',
          'a': 'CAMBRIAN EXPLOSION'},
         {'q': 'EARTH AND SPACE Short Answer: Land that has been frozen for at least two years, including rock or '
               'soil, has what classification?',
          'a': 'PERMAFROST'},
         {'q': 'EARTH AND SPACE Short Answer: List the following four minerals in order of increasing metamorphic '
               'grade:\n'
               '1) Staurolite; 2) Muscovite; 3) Garnet; 4) Chlorite.',
          'a': '4, 2, 3, 1'},
         {'q': 'EARTH AND SPACE Short Answer: Radiometric dating of natural materials is mainly limited by what '
               'property unique to the radionuclide of interest for the specific time scale?',
          'a': 'HALF LIFE'},
         {'q': 'EARTH AND SPACE Short Answer: What type of supernova can leave behind a black hole?', 'a': 'TYPE II'},
         {'q': 'EARTH AND SPACE Short Answer: What is the term for the minimum distance from a planet at which a '
               'satellite can remain intact, without being torn apart by gravitational forces?',
          'a': 'ROCHE LIMIT'},
         {'q': 'EARTH AND SPACE Short Answer: What is the name for the air-lifting process that forces an air mass up '
               'and over a mountain or upland, causing the moisture to rain out on the windward slope and leaving a '
               'rainshadow effect on the leeward slope?',
          'a': 'OROGRAPHIC LIFTING'},
         {'q': 'EARTH AND SPACE Multiple Choice: The Moon always turns the same face toward the Earth, yet small '
               'variations in the visibility of its features appear to take place, such that it appears to rock slowly '
               'backward and forward. What effect accounts for this observed behavior?\n'
               'W) Transient phenomena\n'
               'X) Libration\n'
               'Y) Moonset\n'
               'Z) Earthshine',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: The leading edge of the bowl of the Big Dipper, from bottom to top, '
               'points to what important aid to celestial navigation?',
          'a': 'POLARIS'},
         {'q': 'EARTH AND SPACE Multiple Choice: Tombolos are associated with which of the following?\n'
               'W) Undersea vents\n'
               'X) Islands\n'
               'Y) Volcanoes\n'
               'Z) Wind patterns',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is closest to the percentage of the ocean area '
               'that is represented by continental shelves?\n'
               'W) 10\n'
               'X) 20\n'
               'Y) 30\n'
               'Z) 40',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What is the name for the circular ocean currents that pinch off from '
               'ocean currents in sections, causing drastic changes in sound velocity at the interface?',
          'a': 'EDDIES'},
         {'q': 'EARTH AND SPACE Short Answer: In what constellation can the Crab Nebula be found?', 'a': 'TAURUS'},
         {'q': 'EARTH AND SPACE Short Answer: What is the name for a front that is formed when a cold front overtakes '
               'a warm front and warm air is separated from the cyclonic center?',
          'a': 'OCCLUDED FRONT'},
         {'q': 'EARTH AND SPACE Multiple Choice: The Black Hills of South Dakota is a large dome that has been exposed '
               'due to upwarping followed by erosion. Which of the following rocks would we expect to find in the '
               'innermost core of the Black\n'
               'Hills?\n'
               'W) Shale\n'
               'X) Gypsum\n'
               'Y) Pegmatite\n'
               'Z) Limestone',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: How many times greater, in terms of energy, is a magnitude 6 earthquake '
               'than a magnitude 4 earthquake?',
          'a': '961'},
         {'q': 'EARTH AND SPACE Multiple Choice: The Global Positioning System consists of several operational '
               'satellites in spatially separated orbits around the earth. How many different satellite signals are '
               'required for accurate position, velocity, and time data?\n'
               'W) 2\n'
               'X) 3\n'
               'Y) 4\n'
               'Z) 6',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Kepler’s second law states that in any given period of time, a planet '
               'will have what orbital property stay constant?\n'
               'W) Distance traveled\n'
               'X) Angular distance traveled\n'
               'Y) Area swept\n'
               'Z) Number of rotations',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: What arises in space, thought to be from particle pairs that blink '
               'into existence and promptly annihilate?\n'
               'W) Gravitational potential energy\n'
               'X) Vacuum energy\n'
               'Y) Cherenkov radiation\n'
               'Z) Bremsstrahlung radiation',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: What type of stellar object lies fully within its own Schwarschild '
               'radius?',
          'a': 'BLACK HOLE'},
         {'q': 'EARTH AND SPACE Multiple Choice: Ganymede is more massive than Titan, but only Titan has an '
               'atmosphere.\n'
               'Which of the following correctly explains this?\n'
               "W) Titan's atmosphere is mostly made of heavy gases, like sulfur dioxide, which cannot escape its "
               'gravitational pull\n'
               'X) Titan is significantly colder than Ganymede, preventing its atmosphere from escaping\n'
               'Y) Titan actively replenishes its atmosphere, while Ganymede does not\n'
               'Z) Titan absorbs atmospheric gases from Saturn, while Ganymede does not absorb gases from Jupiter',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Multiple Choice: The eruption of El Chicon had a greater effect on global temperatures '
               'than the eruption of Mount Saint Helens despite being a smaller eruption. Which of the following best '
               'explains why?\n'
               'W) El Chicon emitted much more sulfur dioxide\n'
               'X) El Chicon deposited more heavy ash\n'
               'Y) El Chicon was located more centrally in the hemisphere\n'
               'Z) El Chicon was a more prolonged eruption',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: At which of the following locations on the HR diagram would one find\n'
               'Betelgeuse?\n'
               'W) Top right\n'
               'X) Top left\n'
               'Y) Bottom right\n'
               'Z) Bottom left',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What are the two main non-oxygen elements in coal combustion products '
               'that are responsible for acid rain?',
          'a': 'NITROGEN AND SULFUR'},
         {'q': 'EARTH AND SPACE Multiple Choice: Much of the information we have about the center of the Milky Way was '
               'collected in the radio wavelengths of the electromagnetic spectrum. Which of the following telescopes '
               'could be used to make these images?\n'
               'W) Hubble Space Telescope\n'
               'X) Keck Observatory\n'
               'Y) Chandra Observatory\n'
               'Z) Very Large Array',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: Ground astronomy must be conducted in wavelengths of light that can pass '
               'through\n'
               'Earth’s atmosphere. Aside from visible light, to what other form of electromagnetic radiation is our '
               'atmosphere mostly transparent?',
          'a': 'RADIO'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which variable affecting the speed of sound in the ocean dominates at '
               'very large depths?\n'
               'W) Water Pressure\n'
               'X) Salinity\n'
               'Y) Temperature\n'
               'Z) Biologic density',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: Plutinos are Kuiper belt objects whose orbits are locked in a 3-to-2 '
               'resonance with what planet?',
          'a': 'NEPTUNE'},
         {'q': "EARTH AND SPACE Multiple Choice: A necessary conclusion of Hubble's law is that very-distant galaxies "
               'are moving away from us at speeds faster than the speed of light. Which of the following correctly '
               'explains this observation?\n'
               "W) Hubble's law becomes non-linear for very large distances\n"
               'X) The Hubble constant was originally miscalculated\n'
               'Y) Due to the metric expansion of space, faraway objects can recede from us faster than the speed of '
               'light\n'
               'Z) The proper distance to faraway galaxies does not scale linearly with the Hubble constant',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Cosmologists have recently reembraced the cosmological constant as a '
               'quantity in the Einstein field equations. Which of the following could be a physical explanation for '
               'the cosmological constant?\n'
               'W) Vacuum energy\n'
               'X) Morse energy\n'
               'Y) Cosmic microwave background\n'
               'Z) Dark matter',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: What type of feature is the Moon’s Rupes Recta?\n'
               'W) Fault\n'
               'X) Ridge\n'
               'Y) Bay\n'
               'Z) Valley',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: When corals bleach due to warming seas they expel what symbiotic '
               'organisms, leaving them vulnerable to starvation and disease?\n'
               'W) Chlorella\n'
               'X) Diatoms\n'
               'Y) Zooxanthellae\n'
               'Z) Spirogyra',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of these is true regarding the Sargasso sea?\n'
               'W) It has relatively low biological productivity\n'
               'X) It is adjacent to the Bay of Bengal\n'
               'Y) It is primarily a hypoxic dead zone\n'
               'Z) It has the saltiest ocean water',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: Rank the following three stars in order of increasing surface '
               'temperature:\n'
               '1) Arcturus; 2) Betelgeuse; 3) The Sun.',
          'a': '2, 1, 3'},
         {'q': "EARTH AND SPACE Multiple Choice: Which of the following is closest to the percentage of the Earth's "
               'total surface water contained in ice caps, glaciers, and permanent snow?\n'
               'W) 2\n'
               'X) 13\n'
               'Y) 25\n'
               'Z) 45',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Multiple Choice: The orbital period of Pluto is 248 years. For what percentage of '
               "Pluto's orbital period is it closer to the Sun than Neptune is?\n"
               'W) 8\n'
               'X) 24\n'
               'Y) 37\n'
               'Z) 48',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What is the general term for the formation of mountains?',
          'a': 'OROGENY'},
         {'q': 'EARTH AND SPACE Short Answer: What soil horizon is composed primarily of decaying organic matter?',
          'a': 'O HORIZON'},
         {'q': 'EARTH AND SPACE Multiple Choice: What radioactive element was produced during nuclear-weapons testing '
               'in the mid 1900s and is commonly used by oceanographers to date the age of water masses, but will '
               'decay to normal background levels in the coming decades.\n'
               'W) Carbon-14\n'
               'X) Radon-222\n'
               'Y) Uranium-238\n'
               'Z) Tritium',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Multiple Choice: The key glacier structure formed through annual layering of ice '
               'through cycles of melting and snowfall is called what?\n'
               'W) Ogives\n'
               'X) Primary stratification\n'
               'Y) Longitudinal foliation\n'
               'Z) Transverse crevasses',
          'a': 'X'},
         {'q': "EARTH AND SPACE Multiple Choice: Kepler's third law of planetary motion relates what two parameters of "
               'the orbiting body?\n'
               'W) Solar radiation and distance\n'
               'X) Orbital period and semi-major axis\n'
               'Y) Orbital eccentricity and solar mass\n'
               'Z) Solar mass and mass of orbiting body',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Multiple Choice: Magnetite, pyrite, and galena are mineral examples of which of the '
               'following crystal system types?\n'
               'W) Tetragonal\n'
               'X) Cubic\n'
               'Y) Triclinic\n'
               'Z) Ortho-rhombic',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: How many planes of cleavage does biotite possess?', 'a': 'ONE'},
         {'q': 'EARTH AND SPACE Short Answer: Water-saturated surfaces can behave like liquids during earthquakes. '
               'What is the term for this phenomenon?',
          'a': 'LIQUEFACTION'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is not a unit used by oceanographers to '
               'describe sea water salinity?\n'
               'W) Parts per thousand\n'
               'X) Siemen\n'
               'Y) Practical salinity unit\n'
               'Z) Grams per kilogram',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: Prometheus and Pan both create gaps in Saturn’s rings due to their '
               'gravitational influence. What is the term for this type of satellite?',
          'a': 'SHEPHERD'},
         {'q': 'EARTH AND SPACE Short Answer: The greenhouse effect on Venus is primarily attributed to what gas?',
          'a': 'CARBON DIOXIDE'},
         {'q': 'EARTH AND SPACE Short Answer: To the nearest power of ten, how many times as intense is the light we '
               'receive from a star with apparent magnitude negative 1 as that of another star with apparent magnitude '
               '4?',
          'a': '100'},
         {'q': 'EARTH AND SPACE Short Answer: According to the Stefan-Boltzmann law, a star with surface temperature '
               'in kelvins that is three times that of the Sun would emit how many times as much energy as the Sun?',
          'a': '81'},
         {'q': "EARTH AND SPACE Short Answer: The closed universe is a solution of Einstein's equations of general "
               'relativity in which the mass density of the Universe exceeds what parameter?',
          'a': 'CRITICAL DENSITY'},
         {'q': 'EARTH AND SPACE Short Answer: Identify all of the following three statements that are true of the '
               'inner planets:\n'
               '1) Mercury has an atmosphere of primarily methane; 2) All of the inner planets revolve in the same '
               'direction around the sun; 3) All of the inner planets rotate in the same direction around their axes.',
          'a': '2'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is most directly responsible for ocean water '
               'downwelling in the mid-ocean gyres?\n'
               'W) Ekman transport\n'
               'X) High surface water density\n'
               'Y) High organic carbon content\n'
               'Z) Sea floor spreading',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: What type of extrusive igneous rock is considered intermediate between '
               'basalt and dacite and possesses approximately 60% silica content?',
          'a': 'ANDESITE'},
         {'q': 'EARTH AND SPACE Multiple Choice: What ocean water mass has the oldest carbon-14 age, meaning it has '
               'spent the most time isolated from the atmosphere?\n'
               'W) North Atlantic Deep Water\n'
               'X) Antarctic Bottom Water\n'
               'Y) North Pacific Deep Water\n'
               'Z) Circumpolar Deep Water',
          'a': 'Y'},
         {'q': 'EARTH AND SPACE Short Answer: Multiple Choic Saturn’s rings are mostly composed of which of the '
               'following materials?\n'
               'W) Ice\n'
               'X) Silicates\n'
               'Y) Carbonates\n'
               'Z) Iron',
          'a': 'W) ICE'},
         {'q': 'EARTH AND SPACE Short Answer: The flattening of a protostellar disk in new stars is primarily due to '
               'the conservation of what physical quantity?',
          'a': 'ANGULAR MOMENTUM'},
         {'q': 'EARTH AND SPACE Short Answer: What is the term for the flame-like jets of gas that can be seen at the '
               'edge of the\n'
               "Sun's disk extending into the chromosphere, dissipating after 5 to 15 minutes?",
          'a': 'SPICULES'},
         {'q': 'EARTH AND SPACE Short Answer: The reciprocal of the age of the universe, when converted to kilometers '
               'per second per Megaparsec, approximately equals what physical constant?',
          'a': 'HUBBLE'},
         {'q': 'EARTH AND SPACE Short Answer: Eventually, some stars will begin to fuse helium into carbon. What is '
               'the name of this process?',
          'a': 'TRIPLE ALPHA PROCESS'},
         {'q': 'EARTH AND SPACE Multiple Choice: What is the term for the minimum distance a satellite must orbit from '
               'a planetary body without being torn apart by tidal forces?\n'
               'W) Tidal limit\n'
               'X) Roche limit\n'
               'Y) Ring minimum\n'
               'Z) Moon horizon',
          'a': 'X'},
         {'q': 'EARTH AND SPACE Short Answer: What term is given to the layer of an ocean or lake that extends from '
               'the surface to the depth at which 99 percent of the surface light has been absorbed?',
          'a': 'PHOTIC ZONE'},
         {'q': 'EARTH AND SPACE Short Answer: What is the name for a cloud that looks like a pouch and often forms '
               'hanging down from the underside of the anvil of a cumulonimbus cloud?',
          'a': 'MAMMATUS'},
         {'q': 'EARTH AND SPACE Multiple Choice: Comet McNaught visited in 2007 but is now on a path to leave the '
               'solar system forever. Which of the following best describes its orbit?\n'
               'W) Circular\n'
               'X) Elliptical\n'
               'Y) Parabolic\n'
               'Z) Hyperbolic',
          'a': 'Z'},
         {'q': 'EARTH AND SPACE Short Answer: 21-centimeter radiation is observed throughout much of space because it '
               'is generated from the neutral form of what element?',
          'a': 'HYDROGEN'},
         {'q': 'EARTH AND SPACE Short Answer: Scientists can study solar fusion via observations of certain '
               'near-massless particles that travel through the Sun. What are these particles?',
          'a': 'NEUTRINOS'},
         {'q': 'EARTH AND SPACE Multiple Choice: Which of the following is the best approximation of how much time a '
               'supergiant star can survive by way of silicon fusion?\n'
               'W) 1 day\n'
               'X) 1 year\n'
               'Y) 1 thousand years\n'
               'Y) 1 million years',
          'a': 'W'},
         {'q': 'EARTH AND SPACE Short Answer: In 1967, Jocelyn Bell detected a regularly pulsing radio signal, which '
               'she called\n'
               'LGM. What type of celestial object produced this signal?',
          'a': 'PULSAR'},
         {'q': 'EARTH AND SPACE Short Answer: What carbonate mineral is green in color and contains copper as its main '
               'cation?',
          'a': 'MALACHITE'},
         {'q': 'EARTH AND SPACE Short Answer: Unlike reflectors, refracting telescopes may require an additional lens '
               'to correct for what optical disturbance?',
          'a': 'CHROMATIC ABERRATION'},
         {'q': "EARTH AND SPACE Short Answer: The addition of what metal to the Earth's oceans has been proposed as a "
               'potential way to decrease atmospheric carbon dioxide through the stimulation of photosynthetic '
               'bacteria?',
          'a': 'IRON'}]}


# Initialize data structures (will be loaded from JSON)
current_questions = {}  # Per-channel questions: {channel_id: question}
question_answered = {}  # Track if question has been answered per channel: {channel_id: bool}
user_points = {}  # Dictionary to track points: {user_id: points}

# Load data on startup
load_data()

@bot.event
async def on_ready():
    print(f'{bot.user} is ready!')
    print(f'Loaded {len(current_questions)} active questions, {len(user_points)} users with points')

@bot.command(name='q')
async def ask_question(ctx, subject: str):
    subject = subject.lower()
    if subject not in questions:
        await ctx.send(f'Invalid subject! Use: phy, math, bio, ess, chem, or energy')
        return
    
    question = random.choice(questions[subject])
    channel_id = ctx.channel.id
    
    # Store question per channel
    current_questions[channel_id] = question
    question_answered[channel_id] = False  # Reset answered status when new question is asked
    save_data()  # Save after updating
    await ctx.send(f'**Question:**\n{question["q"]}')

from groq import Groq

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@bot.command(name='a')
async def check_answer(ctx, *, answer: str):
    channel_id = ctx.channel.id
    
    # Check if there's an active question in this channel
    if channel_id not in current_questions:
        await ctx.send('No active question in this channel! Use `-q <subject>` to ask a question')
        return
    
    # Check if question has already been answered in this channel
    if question_answered.get(channel_id, False):
        await ctx.send('❌ This question has already been answered! Wait for a new question.')
        return
    
    # Get the question for this channel
    correct = current_questions[channel_id]['a']
    
    # Mark question as answered immediately (before processing) so no one else can answer
    question_answered[channel_id] = True
    save_data()  # Save after marking as answered
    user_answer = answer.strip().upper()
    correct_answer = correct.upper()
    
    prompt = f"Is the answer {user_answer} reasonably correct? Ignore formatting, syntax, etc. Synonyms are allowed. The correct answer is {correct_answer}. Output one word: yes or no"

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
        {
            "role": "user",
            "content": prompt
        }
        ],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        stream=False,
        stop=None
    )

    response = completion.choices[0].message.content
    
    # Initialize user points if they don't exist
    if ctx.author.id not in user_points:
        user_points[ctx.author.id] = 0
    
    if response.lower() == 'yes':
        user_points[ctx.author.id] += 10
        save_data()  # Save after updating points
        await ctx.send(f'✅ **{ctx.author.name}** got it first! Correct answer: {correct}\n**+10 points!** Total: {user_points[ctx.author.id]} points')
    else:
        user_points[ctx.author.id] -= 5
        save_data()  # Save after updating points
        await ctx.send(f'❌ **{ctx.author.name}** answered first but was incorrect. The correct answer is: {correct}\n**-5 points.** Total: {user_points[ctx.author.id]} points')

# Optional: Add a command to check points
@bot.command(name='points')
async def check_points(ctx):
    if ctx.author.id not in user_points:
        await ctx.send('You have 0 points!')
    else:
        await ctx.send(f'You have {user_points[ctx.author.id]} points')

# Optional: Add a leaderboard command
@bot.command(name='leaderboard')
async def leaderboard(ctx):
    if not user_points:
        await ctx.send('No one has any points yet!')
        return
    
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "**Leaderboard**\n"
    
    for i, (user_id, points) in enumerate(sorted_users[:10], 1):
        user = await bot.fetch_user(user_id)
        leaderboard_text += f"{i}. {user.name}: {points} points\n"
    
    await ctx.send(leaderboard_text)

@bot.command(name='commands')
async def commands(ctx):
    await ctx.send('**Commands**\n-q <subject> (phy, bio, chem, math, ess, energy) - Ask a question\n-a <answer> - Check your answer\n-points - Check your points\n-leaderboard - Check the leaderboard')

token = str(os.getenv('DISCORD_BOT_TOKEN'))
if not token:
    print('Error: DISCORD_BOT_TOKEN environment variable is not set!')
    print('Please set it using: export DISCORD_BOT_TOKEN="your_token_here"')
    exit(1)

bot.run(token)

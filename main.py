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

questions = {'phy': [{'q': 'PHYSICS Short Answer: Planck was able to describe the color change of black bodies at different '
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
             'a': 'COPPER'}],
 'chem': [{'q': 'CHEMISTRY Short Answer: Given the percentages by mass of different elements in a compound, identify '
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
          'a': 'X'}],
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
           'a': '2pi - 4√2'}],
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
          'a': 'X'}]}


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
    await ctx.send('**Commands**\n-q <subject> (phy, bio, chem, math, ess, energy)- Ask a question\n-a <answer> - Check your answer\n-points - Check your points\n-leaderboard - Check the leaderboard')

token = str(os.getenv('DISCORD_BOT_TOKEN'))
if not token:
    print('Error: DISCORD_BOT_TOKEN environment variable is not set!')
    print('Please set it using: export DISCORD_BOT_TOKEN="your_token_here"')
    exit(1)

bot.run(token)
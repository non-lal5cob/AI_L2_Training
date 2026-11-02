# Drone Flight Control System --- Requirements Specification

**Document ID:** DFC-SRS-001\
**Version:** 1.0\
**Status:** Initial baseline\
**Date:** 2 November 2026

## 1. Purpose

This document defines a baseline set of system and software requirements
for a drone flight control system (FCS). It is intended to support
system design, implementation, integration, and verification.

The requirements are written for a **small multirotor unmanned
aircraft** (for example, a quadcopter) with an onboard flight
controller, inertial sensors, navigation capability, electronic speed
controllers (ESCs), a battery, and a ground control station (GCS).

This is a generic engineering starting point, not a design approval or
certification basis. The requirements must be tailored to the aircraft,
operating environment, applicable regulations, hazard analysis, and
selected hardware.

## 2. Scope

The flight control system is responsible for: - Acquiring and validating
sensor data. - Estimating aircraft attitude, angular rates, and (where
equipped) position and velocity. - Stabilizing the aircraft and
controlling its movement. - Converting pilot or mission commands into
motor/actuator commands. - Managing arming, disarming, flight modes, and
failsafe responses. - Monitoring system health and reporting status and
faults. - Supporting safe startup, shutdown, and in-flight fault
handling.

The FCS does not, by itself, define the complete airworthiness of the
drone, the security of the radio link, the ground control station
design, or regulatory permissions to fly.

## 3. Assumptions and design inputs

1.  The baseline aircraft is a multirotor with independently controlled
    electric motors.
2.  The flight controller includes at least an IMU containing gyroscope
    and accelerometer sensors.
3.  A magnetometer, barometer, GNSS receiver, range sensor, or
    optical-flow sensor may be installed depending on the selected
    functions.
4.  The aircraft has a command link to a pilot-operated GCS or radio
    controller.
5.  The battery and ESCs provide electrical and status information to
    the FCS where supported.
6.  Numerical limits such as maximum speed, tilt angle, altitude,
    control-loop rate, and battery thresholds shall be defined by the
    aircraft-level design and verified through analysis and test.
7.  Loss of a sensor, actuator, power source, or communication link
    shall be addressed by a system safety analysis. The response must
    not be assumed safe for every aircraft configuration.

## 4. Terms and abbreviations

  Term   Meaning
  ------ -----------------------------------------------
  FCS    Flight Control System
  FCU    Flight Control Unit / flight controller
  GCS    Ground Control Station
  IMU    Inertial Measurement Unit
  GNSS   Global Navigation Satellite System
  ESC    Electronic Speed Controller
  RC     Radio-control command link
  PID    Proportional--Integral--Derivative controller
  RTL    Return to Launch
  FMEA   Failure Modes and Effects Analysis
  HIL    Hardware-in-the-Loop
  SIL    Software-in-the-Loop

## 5. System operating modes

The design shall define and implement only the modes supported by the
aircraft configuration. The following are candidate modes:

  -----------------------------------------------------------------------
  Mode                                Description
  ----------------------------------- -----------------------------------
  Power-off                           Flight controller is not powered.

  Initialization                      Hardware, software, sensors, and
                                      configuration are initialized and
                                      checked.

  Standby / Disarmed                  Motors are inhibited; system
                                      monitors readiness and status.

  Armed / Ready                       Flight control is active and motor
                                      outputs may be enabled under
                                      defined conditions.

  Manual / Stabilized                 Pilot commands control attitude or
                                      angular rate, with stabilization as
                                      configured.

  Altitude Hold                       Controller regulates altitude using
                                      a validated altitude source.

  Position Hold                       Controller regulates horizontal
                                      position using valid navigation or
                                      positioning data.

  Autonomous Mission                  Controller executes an approved,
                                      uploaded mission.

  Return to Launch                    Controller executes the configured
                                      return procedure when its
                                      prerequisites are satisfied.

  Landing                             Controller performs a controlled
                                      descent and landing.

  Failsafe                            Controller executes the response
                                      selected for the detected fault or
                                      loss of control input.

  Emergency Stop                      A defined emergency
                                      motor-inhibition response, where
                                      the aircraft safety concept permits
                                      it.
  -----------------------------------------------------------------------

Transitions, entry conditions, exit conditions, priorities, and
prohibited transitions shall be specified in a state-machine design.

## 6. Functional requirements

### 6.1 Startup, initialization, and configuration

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-001               The FCS shall execute a Test
                          defined startup         
                          sequence after power is 
                          applied.                

  FCS-F-002               The FCS shall           Test
                          initialize all          
                          configured sensors and  
                          actuator interfaces     
                          before declaring the    
                          system ready.           

  FCS-F-003               The FCS shall perform   Test / Analysis
                          startup self-tests for  
                          supported processor,    
                          memory, sensor, and     
                          communication           
                          functions.              

  FCS-F-004               The FCS shall inhibit   Test
                          motor arming when a     
                          safety-critical startup 
                          check fails.            

  FCS-F-005               The FCS shall validate  Test
                          configuration data      
                          before using it for     
                          flight control.         

  FCS-F-006               The FCS shall detect    Test
                          missing, corrupted,     
                          out-of-range, or        
                          unsupported             
                          configuration           
                          parameters.             

  FCS-F-007               The FCS shall provide a Test
                          clear readiness or      
                          inhibit status to the   
                          GCS or pilot interface. 

  FCS-F-008               The FCS shall support   Test
                          controlled calibration  
                          procedures for the      
                          sensors that require    
                          calibration.            
  -----------------------------------------------------------------------

### 6.2 Sensor acquisition and validation

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-010               The FCS shall acquire   Test
                          gyroscope and           
                          accelerometer data at   
                          rates sufficient for    
                          the specified control   
                          bandwidth.              

  FCS-F-011               The FCS shall timestamp Test / Analysis
                          or otherwise time-align 
                          sensor samples used     
                          together in state       
                          estimation.             

  FCS-F-012               The FCS shall detect    Test
                          sensor data that is     
                          stale, missing,         
                          invalid, or outside     
                          configured physical     
                          limits.                 

  FCS-F-013               The FCS shall detect    Test
                          configured sensor       
                          communication failures. 

  FCS-F-014               The FCS shall estimate  Test
                          aircraft attitude and   
                          angular rates from      
                          available inertial      
                          measurements.           

  FCS-F-015               Where a barometer is    Test
                          installed, the FCS      
                          shall estimate altitude 
                          using the configured    
                          barometric processing.  

  FCS-F-016               Where GNSS is           Test
                          installed, the FCS      
                          shall evaluate GNSS     
                          validity and report     
                          position, velocity, and 
                          fix quality as          
                          available.              

  FCS-F-017               Where a magnetometer is Test
                          installed, the FCS      
                          shall evaluate magnetic 
                          measurement validity    
                          before using heading    
                          data.                   

  FCS-F-018               The FCS shall identify  Test
                          which navigation and    
                          altitude sources are    
                          valid and available to  
                          each flight mode.       

  FCS-F-019               The FCS shall prevent   Test
                          invalid or unavailable  
                          sensor data from being  
                          silently treated as     
                          valid input.            
  -----------------------------------------------------------------------

### 6.3 State estimation

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-020               The FCS shall calculate Test
                          the state variables     
                          required by each        
                          enabled flight mode.    

  FCS-F-021               The FCS shall provide   Test
                          attitude and            
                          angular-rate estimates  
                          to the control          
                          functions within the    
                          specified latency.      

  FCS-F-022               The FCS shall provide   Test
                          position, velocity, and 
                          altitude estimates when 
                          the required sensors    
                          are valid and the       
                          relevant mode is        
                          enabled.                

  FCS-F-023               The FCS shall provide   Test
                          an estimate-validity or 
                          confidence status for   
                          navigation outputs.     

  FCS-F-024               The FCS shall detect    Test
                          state-estimation        
                          conditions that exceed  
                          configured validity     
                          limits.                 

  FCS-F-025               The FCS shall           Test
                          transition to a defined 
                          degraded or failsafe    
                          behavior when required  
                          state estimates become  
                          invalid.                
  -----------------------------------------------------------------------

### 6.4 Flight control and stabilization

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-030               The FCS shall stabilize Test
                          aircraft angular rates  
                          using the configured    
                          rate-control function.  

  FCS-F-031               The FCS shall control   Test
                          aircraft attitude in    
                          flight modes that       
                          command attitude.       

  FCS-F-032               The FCS shall convert   Test
                          pilot or mission        
                          setpoints into bounded  
                          control demands.        

  FCS-F-033               The FCS shall limit     Test
                          control demands to      
                          aircraft-configured     
                          operational limits.     

  FCS-F-034               The FCS shall allocate  Test
                          control demands to the  
                          available motors        
                          according to the        
                          configured airframe     
                          geometry.               

  FCS-F-035               The FCS shall constrain Test
                          motor commands to the   
                          valid command range     
                          defined for the ESC     
                          interface.              

  FCS-F-036               The FCS shall apply     Test / Analysis
                          configured anti-windup  
                          or equivalent           
                          protection to integral  
                          control terms.          

  FCS-F-037               The FCS shall detect    Test
                          and report control      
                          saturation when the     
                          actuator allocation     
                          cannot meet requested   
                          control demands.        

  FCS-F-038               The FCS shall use       Test
                          defined behavior for    
                          invalid, missing, or    
                          out-of-range pilot      
                          setpoints.              

  FCS-F-039               The FCS shall prevent   Test
                          abrupt setpoint changes 
                          beyond configured       
                          transition limits.      
  -----------------------------------------------------------------------

### 6.5 Altitude and position control

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-040               When Altitude Hold is   Test
                          enabled, the FCS shall  
                          regulate altitude using 
                          a valid configured      
                          altitude estimate.      

  FCS-F-041               The FCS shall reject or Test
                          inhibit Altitude Hold   
                          when no valid altitude  
                          source is available.    

  FCS-F-042               When Position Hold is   Test
                          enabled, the FCS shall  
                          regulate horizontal     
                          position using valid    
                          position and velocity   
                          estimates.              

  FCS-F-043               The FCS shall reject or Test
                          inhibit Position Hold   
                          when the required       
                          navigation solution is  
                          invalid.                

  FCS-F-044               The FCS shall enforce   Test
                          configured altitude,    
                          speed, and geofence     
                          limits when those       
                          functions are enabled.  

  FCS-F-045               The FCS shall define    Test
                          behavior for temporary  
                          degradation or loss of  
                          navigation data during  
                          position-controlled     
                          flight.                 
  -----------------------------------------------------------------------

### 6.6 Pilot command and mission handling

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-050               The FCS shall receive   Test
                          pilot commands through  
                          the configured command  
                          interface.              

  FCS-F-051               The FCS shall validate  Test
                          command freshness,      
                          range, and format       
                          before accepting a      
                          command.                

  FCS-F-052               The FCS shall map       Test
                          accepted pilot commands 
                          to the active flight    
                          mode's control          
                          setpoints.              

  FCS-F-053               The FCS shall accept an Test
                          autonomous mission only 
                          after validating its    
                          format and configured   
                          operational             
                          constraints.            

  FCS-F-054               The FCS shall execute   Test
                          mission commands in the 
                          defined sequence and    
                          report mission          
                          progress.               

  FCS-F-055               The FCS shall reject    Test
                          mission commands that   
                          violate configured      
                          limits or are           
                          unsupported by the      
                          aircraft.               

  FCS-F-056               The FCS shall provide a Test
                          defined means to pause, 
                          abort, or otherwise     
                          safely terminate an     
                          autonomous mission.     
  -----------------------------------------------------------------------

### 6.7 Arming, disarming, takeoff, and landing

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-060               The FCS shall implement Test
                          explicit arming and     
                          disarming states.       

  FCS-F-061               The FCS shall permit    Test
                          arming only when all    
                          configured arming       
                          conditions are          
                          satisfied.              

  FCS-F-062               The FCS shall provide   Test
                          the reason when arming  
                          is inhibited.           

  FCS-F-063               The FCS shall prevent   Test
                          unintended motor        
                          activation while        
                          disarmed.               

  FCS-F-064               The FCS shall implement Test
                          a controlled takeoff    
                          function where          
                          supported.              

  FCS-F-065               The FCS shall implement Test
                          a controlled landing    
                          function where          
                          supported.              

  FCS-F-066               The FCS shall define    Test
                          motor-output behavior   
                          during landing,         
                          touchdown detection,    
                          and disarming.          

  FCS-F-067               The FCS shall not       Analysis / Test
                          automatically disarm in 
                          flight unless the       
                          approved safety concept 
                          explicitly requires     
                          that response.          
  -----------------------------------------------------------------------

### 6.8 Failsafe and fault management

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-070               The FCS shall monitor   Test
                          the pilot command link  
                          for loss, timeout, and  
                          invalid data.           

  FCS-F-071               The FCS shall detect    Test
                          battery conditions that 
                          cross configured        
                          warning and critical    
                          thresholds.             

  FCS-F-072               The FCS shall detect    Test
                          configured sensor,      
                          estimator,              
                          actuator-interface, and 
                          internal software       
                          faults.                 

  FCS-F-073               The FCS shall associate Analysis / Test
                          each detected fault     
                          with a defined severity 
                          and response.           

  FCS-F-074               The FCS shall execute   Test
                          the approved failsafe   
                          response for loss of    
                          pilot command input.    

  FCS-F-075               The FCS shall execute   Test
                          the approved response   
                          for critical battery    
                          conditions.             

  FCS-F-076               The FCS shall execute a Test
                          defined degraded-mode   
                          or failsafe response    
                          when a flight-critical  
                          sensor becomes invalid. 

  FCS-F-077               The FCS shall report    Test
                          detected faults and the 
                          active failsafe state   
                          to the pilot interface  
                          when communication is   
                          available.              

  FCS-F-078               The FCS shall record    Test
                          fault occurrence and    
                          relevant status         
                          information for         
                          post-flight analysis.   

  FCS-F-079               The FCS shall prevent   Test
                          automatic recovery from 
                          a critical fault unless 
                          recovery conditions are 
                          explicitly defined and  
                          satisfied.              

  FCS-F-080               The FCS shall define    Analysis / Test
                          priority and            
                          arbitration when        
                          multiple faults occur   
                          simultaneously.         
  -----------------------------------------------------------------------

### 6.9 Return to Launch and emergency behavior

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-F-090               Where RTL is supported, Test
                          the FCS shall validate  
                          the required home       
                          position and navigation 
                          solution before         
                          initiating RTL.         

  FCS-F-091               The FCS shall execute   Test
                          the configured RTL      
                          route, altitude, and    
                          termination behavior.   

  FCS-F-092               The FCS shall inhibit   Test
                          or select an alternate  
                          response when RTL       
                          prerequisites are not   
                          met.                    

  FCS-F-093               The FCS shall define    Test
                          behavior if navigation  
                          is lost during RTL.     

  FCS-F-094               The FCS shall implement Analysis / Test
                          emergency behavior in   
                          accordance with the     
                          aircraft safety         
                          assessment.             
  -----------------------------------------------------------------------

### 6.10 Health monitoring, logging, and communication

  -------------------------------------------------------------------------
  ID                      Requirement               Verification
  ----------------------- ------------------------- -----------------------
  FCS-F-100               The FCS shall provide     Test
                          system health and flight  
                          status to the GCS or      
                          pilot interface.          

  FCS-F-101               The FCS shall report      Test
                          sensor validity, battery  
                          status, active mode,      
                          arming state, and         
                          failsafe state where      
                          supported.                

  FCS-F-102               The FCS shall log         Test
                          flight-critical events    
                          with timestamps or an     
                          equivalent ordering       
                          mechanism.                

  FCS-F-103               The FCS shall retain      Test
                          fault and flight logs     
                          across normal power       
                          cycles, where             
                          non-volatile storage is   
                          provided.                 

  FCS-F-104               The FCS shall detect      Test
                          communication-interface   
                          errors supported by the   
                          hardware and protocol.    

  FCS-F-105               The FCS shall reject      Test
                          malformed or unsupported  
                          messages.                 

  FCS-F-106               The FCS shall define      Test
                          behavior when telemetry   
                          communication is lost     
                          while the pilot command   
                          link remains available.   
  -------------------------------------------------------------------------

## 7. Non-functional requirements

Numerical targets shall be completed in the project-specific requirement
baseline.

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-NF-001              The FCS shall complete  Test / Analysis
                          each control cycle      
                          within its allocated    
                          execution-time budget.  

  FCS-NF-002              The FCS shall meet the  Test
                          defined maximum         
                          end-to-end latency from 
                          command or sensor input 
                          to actuator output.     

  FCS-NF-003              The FCS shall maintain  Test
                          the specified           
                          control-loop frequency  
                          under worst-case        
                          supported processing    
                          load.                   

  FCS-NF-004              The FCS shall meet the  Test
                          aircraft-defined        
                          attitude, altitude, and 
                          position tracking       
                          performance limits.     

  FCS-NF-005              The FCS shall operate   Test
                          within the specified    
                          supply-voltage and      
                          power-consumption       
                          limits.                 

  FCS-NF-006              The FCS shall operate   Test
                          over the specified      
                          temperature, vibration, 
                          humidity, and           
                          environmental ranges.   

  FCS-NF-007              The FCS hardware and    Test
                          software shall tolerate 
                          the electromagnetic     
                          environment defined for 
                          the aircraft.           

  FCS-NF-008              The FCS shall provide   Test / Analysis
                          deterministic handling  
                          of control tasks and    
                          safety-related events   
                          within specified timing 
                          limits.                 

  FCS-NF-009              The FCS shall detect    Test
                          and safely handle       
                          processor overload,     
                          task deadline misses,   
                          and watchdog events.    

  FCS-NF-010              The FCS software shall  Inspection
                          be modular and          
                          maintainable, with      
                          defined interfaces      
                          between drivers,        
                          estimation, control,    
                          mode management, and    
                          communication.          

  FCS-NF-011              The FCS shall support   Inspection
                          traceability from       
                          system requirements to  
                          software requirements,  
                          design elements, and    
                          verification results.   

  FCS-NF-012              The FCS shall support   Inspection
                          reproducible software   
                          builds and              
                          configuration           
                          identification.         

  FCS-NF-013              The FCS shall protect   Test
                          safety-critical         
                          configuration data      
                          against unintended      
                          modification and detect 
                          invalid configuration.  

  FCS-NF-014              The FCS shall minimize  Test / Analysis
                          unnecessary telemetry   
                          and logging load so     
                          that control-task       
                          timing is not           
                          compromised.            

  FCS-NF-015              The FCS shall provide   Test / Inspection
                          diagnostic information  
                          sufficient to support   
                          fault investigation     
                          without exposing unsafe 
                          control interfaces.     
  -----------------------------------------------------------------------

## 8. Safety requirements

These are preliminary safety requirements. A formal hazard analysis (for
example, FHA, FMEA, FTA, or equivalent) is required to derive
aircraft-specific safety objectives and integrity levels.

  -----------------------------------------------------------------------
  ID                      Requirement             Verification
  ----------------------- ----------------------- -----------------------
  FCS-S-001               The FCS shall prevent   Test
                          motor activation unless 
                          the defined arming      
                          conditions are          
                          satisfied.              

  FCS-S-002               The FCS shall detect    Test
                          loss of valid control   
                          input within the        
                          allocated detection     
                          time.                   

  FCS-S-003               The FCS shall           Test
                          transition to the       
                          aircraft-approved       
                          response following loss 
                          of valid control input. 

  FCS-S-004               The FCS shall detect    Test
                          invalid flight-critical 
                          sensor data within the  
                          allocated detection     
                          time.                   

  FCS-S-005               The FCS shall prevent a Analysis / Test
                          single detected sensor  
                          fault from causing      
                          unbounded control       
                          output.                 

  FCS-S-006               The FCS shall constrain Test
                          actuator commands to    
                          approved electrical and 
                          mechanical limits.      

  FCS-S-007               The FCS shall detect    Test / Analysis
                          processor execution     
                          failure using an        
                          independent or          
                          appropriately designed  
                          monitoring mechanism.   

  FCS-S-008               The FCS shall enter a   Test
                          defined safe or         
                          degraded state          
                          following a watchdog    
                          reset or unrecoverable  
                          software fault.         

  FCS-S-009               The FCS shall ensure    Analysis / Test
                          that failsafe actions   
                          are prioritized over    
                          non-safety-critical     
                          mission and telemetry   
                          functions.              

  FCS-S-010               The FCS shall not rely  Test
                          on an unavailable       
                          navigation source to    
                          execute a               
                          navigation-dependent    
                          failsafe action.        

  FCS-S-011               The FCS shall define    Test / Analysis
                          safe behavior for loss  
                          of each power input and 
                          brownout condition.     

  FCS-S-012               The FCS shall prevent   Test
                          unintended changes to   
                          safety-critical         
                          parameters during       
                          flight.                 

  FCS-S-013               The FCS shall define    Analysis / Test
                          and verify behavior for 
                          simultaneous and        
                          cascading faults.       

  FCS-S-014               The FCS shall provide a Test
                          means to identify the   
                          active safety mode and  
                          the reason for its      
                          activation.             
  -----------------------------------------------------------------------

**Important:** "Safe state" is aircraft-dependent. Stopping all motors
may cause an uncontrolled fall and is not automatically a safe response.
The correct response must be selected through hazard analysis for the
aircraft and operating environment.

## 9. External interface requirements

### 9.1 Sensor interfaces

The design shall define, for every sensor: - Electrical interface and
voltage levels. - Communication protocol and bus address, where
applicable. - Data format, units, scaling, and sign convention. -
Sampling rate and maximum data age. - Startup and calibration
behavior. - Validity, timeout, and fault-detection criteria.

### 9.2 Actuator / ESC interfaces

The design shall define: - ESC command protocol and electrical levels. -
Command update rate and timeout behavior. - Minimum, maximum, idle, and
disarmed command values. - Motor order, rotation direction, and airframe
mixing configuration. - ESC status and fault feedback, if available. -
Startup, arming, and shutdown sequencing.

### 9.3 Pilot command and telemetry interfaces

The design shall define: - Physical and logical interfaces. - Message
identifiers, formats, units, and scaling. - Command validity and timeout
rules. - Authentication or pairing provisions, where applicable. -
Telemetry update rates and priority. - Behavior for link degradation,
loss, and recovery.

### 9.4 Power and battery interface

The design shall define: - Supported voltage and current measurement
ranges. - Measurement accuracy and update rate. - Battery chemistry and
cell-count configuration. - Warning and critical thresholds, including
required margins. - Behavior for measurement failure or implausible
readings. - Brownout and power-loss behavior.

## 10. Preliminary performance parameters to be specified

The project shall assign measurable values to at least the following
parameters. Values must be derived from aircraft dynamics, propulsion
sizing, sensor capability, mission profile, and safety analysis rather
than copied from a generic template.

  -----------------------------------------------------------------------
  Parameter               Project value           Notes
  ----------------------- ----------------------- -----------------------
  Maximum takeoff mass    TBD                     Aircraft-level limit

  Maximum flight speed    TBD                     By operating mode

  Maximum climb / descent TBD                     Include mode-specific
  rate                                            limits

  Maximum tilt angle      TBD                     By flight mode

  Attitude tracking error TBD                     Define test conditions

  Angular-rate tracking   TBD                     Define bandwidth and
  error                                           conditions

  Altitude-hold error     TBD                     Requires valid altitude
                                                  source

  Position-hold error     TBD                     Requires valid
                                                  navigation source

  IMU sampling rate       TBD                     Sensor and control
                                                  design input

  Rate-control loop       TBD                     Include worst-case
  frequency                                       execution load

  Attitude-control loop   TBD                     Include worst-case
  frequency                                       execution load

  Command-to-actuator     TBD                     End-to-end measurement
  latency                                         

  Sensor timeout limits   TBD                     Per sensor/interface

  RC loss detection time  TBD                     Link and protocol
                                                  dependent

  Battery warning         TBD                     Battery supplier and
  threshold                                       mission dependent

  Battery critical        TBD                     Safety analysis
  threshold                                       dependent

  Operating temperature   TBD                     Hardware qualification
                                                  range

  Vibration environment   TBD                     Propulsion and airframe
                                                  dependent

  Flight endurance        TBD                     Aircraft-level
                                                  requirement
  -----------------------------------------------------------------------

## 11. Verification strategy

Each requirement shall have one or more verification methods:

-   **Inspection:** review of source code, design, configuration,
    interface definitions, or documentation.
-   **Analysis:** calculations, timing analysis, safety analysis, or
    model-based evidence.
-   **Test:** execution on target hardware, bench setup, SIL, HIL, or
    controlled flight test.
-   **Demonstration:** observable operation in a representative
    environment.

Recommended verification stages:

1.  **Unit testing:** sensor drivers, protocol handlers, estimators,
    controllers, limiters, and state machines.
2.  **SIL testing:** control algorithms and mode transitions in a
    simulated vehicle model.
3.  **HIL testing:** target flight controller connected to simulated
    sensors and vehicle dynamics.
4.  **Bench testing:** power-up, arming inhibition, motor output checks,
    communication, and fault injection with propellers removed.
5.  **Ground testing:** restrained or otherwise controlled validation of
    propulsion and sensor behavior.
6.  **Flight testing:** incremental envelope expansion in a controlled
    test area, after required safety reviews and ground tests.

Flight tests shall be planned and conducted by qualified personnel under
applicable local regulations and an approved test procedure. Initial
testing should use a controlled environment, conservative limits, and a
documented abort plan.

## 12. Fault-injection test cases

  -----------------------------------------------------------------------
  Test ID                 Injected condition      Expected result
  ----------------------- ----------------------- -----------------------
  FCS-T-001               IMU data stops updating Fault detected;
                                                  affected modes
                                                  inhibited or approved
                                                  degraded response
                                                  selected

  FCS-T-002               IMU measurement exceeds Sample rejected or
                          configured range        handled as invalid;
                                                  fault reported

  FCS-T-003               GNSS fix becomes        Position-dependent mode
                          invalid during Position exits or transitions
                          Hold                    according to approved
                                                  logic

  FCS-T-004               Pilot command link is   Loss detected within
                          disconnected            allocated time;
                                                  configured failsafe
                                                  executed

  FCS-T-005               Telemetry link is       Flight control remains
                          disconnected while      according to design;
                          pilot link remains      telemetry loss is
                          valid                   reported when possible

  FCS-T-006               Battery voltage crosses Warning is generated
                          warning threshold       and reported

  FCS-T-007               Battery voltage crosses Approved
                          critical threshold      critical-battery
                                                  response is executed

  FCS-T-008               Invalid configuration   Startup or affected
                          value is loaded         function is inhibited;
                                                  diagnostic is provided

  FCS-T-009               Control task misses its Timing fault is
                          deadline                detected and defined
                                                  recovery/failsafe
                                                  behavior occurs

  FCS-T-010               Watchdog reset occurs   Restart and post-reset
                                                  behavior follow the
                                                  approved safety concept

  FCS-T-011               One ESC or motor        Fault is detected and
                          feedback reports a      aircraft-specific
                          fault, if feedback is   response is executed
                          available               

  FCS-T-012               Two faults occur at the Fault priority and
                          same time               arbitration follow the
                                                  defined safety strategy
  -----------------------------------------------------------------------

## 13. Requirements quality and traceability rules

Every project requirement shall: 1. Have a unique, stable identifier. 2.
State one requirement only. 3. Use "shall" for a mandatory requirement.
4. Be clear, unambiguous, and technically feasible. 5. Be verifiable by
inspection, analysis, test, or demonstration. 6. Include measurable
limits where performance is involved. 7. Identify applicable operating
modes and preconditions. 8. Trace to its parent system requirement or
safety objective. 9. Have an assigned verification method and acceptance
criteria. 10. Be reviewed for conflicts, duplication, and unintended
interactions.

Suggested traceability columns for a project requirements database:

  ------------------------------------------------------------------------------------------------------
  Requirement   Parent   Requirement   Rationale        Safety      Verification   Acceptance   Status
  ID            ID       text                           relevance   method         criteria     
  ------------- -------- ------------- ---------------- ----------- -------------- ------------ --------
  FCS-F-001     TBD      The FCS shall Controlled       TBD         Test           TBD          Draft
                         execute a     initialization                                           
                         defined                                                                
                         startup                                                                
                         sequence                                                               
                         after power                                                            
                         is applied.                                                            

  ------------------------------------------------------------------------------------------------------

## 14. Open items for project tailoring

The following decisions are required before this baseline can be treated
as a project-specific specification:

-   Aircraft type: quadcopter, hexacopter, octocopter, fixed-wing, or
    VTOL.
-   Intended use: hobby, inspection, mapping, agriculture, delivery, or
    another mission.
-   Maximum takeoff mass and propulsion configuration.
-   Flight controller processor and hardware architecture.
-   Sensor set and redundancy strategy.
-   Manual, assisted, and autonomous modes to be supported.
-   Navigation source and expected GNSS-denied behavior.
-   Required flight envelope and environmental limits.
-   Command and telemetry protocols.
-   Battery chemistry, capacity, monitoring capability, and thresholds.
-   Required fault tolerance and safety objectives.
-   Applicable aviation regulations and any intended certification
    standard.

## 15. References and standards to consider

Select standards based on the intended aircraft category, operating
jurisdiction, and assurance objectives. Potential references include:

-   Applicable national aviation authority rules and operational
    guidance.
-   ISO 21384 series --- Unmanned aircraft systems, where applicable.
-   ASTM standards applicable to unmanned aircraft systems and
    operations, where applicable.
-   RTCA DO-178C --- Software Considerations in Airborne Systems and
    Equipment Certification, if an applicable certification basis
    requires or adopts it.
-   RTCA DO-254 --- Design Assurance Guidance for Airborne Electronic
    Hardware, if applicable.
-   SAE ARP4754A / ARP4754B --- Development of Civil Aircraft and
    Systems, where applicable.
-   SAE ARP4761 / ARP4761A --- Safety Assessment Process, where
    applicable.

The applicability and current editions of standards must be confirmed
for the target market and certification basis. Listing a standard here
does not imply compliance.

------------------------------------------------------------------------

**End of document**

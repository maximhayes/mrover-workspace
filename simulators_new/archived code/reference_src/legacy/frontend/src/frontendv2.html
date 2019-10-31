<!DOCTYPE html>
<head>
    <link rel="stylesheet" type="text/css" href="../css/frontend.css"/>
    <script src='../js/vue.js'></script>
</head> 
<body>
    <h1>Simulator V2</h1>
    <div class="container">
        <div class="field">
            <h2>Field</h2>
        </div>
        <div class="location_container" style="order:2">
            <div>
                <h2>Waypoints:</h2>
                <ul class="item_list"></ul>
            </div>
            <div>
                <h2>Tennis Balls:</h2>
                <ul class="item_list"></ul>
            </div>
        </div>
        <div class="location_container" style="order:3">
            <h2>Rocks:</h2>
            <ul class="item_list"></ul>
        </div>
        <div class="status, location_container" style="order:4">
            <h2>Status:</h2>
            <div>
                <h3>Rover Odometry</h3>
                <ul>
                    <li>Latitude: <span>123</span></li>
                    <li>Longitude: <span>456</span></li>
                    <li>Bearing: <span>789</span></li>
            </div>  
            <div>
                <h3>Joystick Inputs</h3>
                <ul>
                    <li>Translational: <span>987</span></li>
                    <li>Rotational: <span>654</span></li>
                </ul>
            </div>
            <div>
                <h3>Simulation Progress</h3>
                <ul>
                    <li>Navigation State: <span>Navig8ing</span></li>
                    <li>Completed Waypoints: <span>6/66</span></li>
                    <li>Missed Waypoints: <span>1123581347/-1</span></li>
                    <li>Found Tennis Balls: <span>3.1415*2</span></li>
                </ul>
            </div>          
        </div>
        <div class="control_bar">
            <h2>Control Panel:</h2>
            <h3>Field Parameters</h3>
            <div class="field_rad">
                <p>Field Radius: <span>rad_Var</span></p>
                <p>Changes radius of the field  </p>
                <input type="text">
                <button>Change Radius</button>
                <p>Field Noise: <span>noise_Var</span></p>
                <p>Simulates noise and slight error accumulation based on terrain and nautral instrumentation error. Default is 1.</p>
                <input type="text" value="1"><button>Change Noise Multiplier</button>
            </div>
            <div class="placement_buttons">
                <h3>Add/Remove Objects</h3>
                <div>
                    <input name="placement" type="radio" checked><p>Place Waypoint</p>
                </div>
                <div>
                    <input name="placement" type="radio"><p>Place Tennis Ball</p>
                </div>
                <div>
                    <input name="placement" type="radio"><p>Place Rock</p>
                </div>
                <button type="button">Clear All Objects</button>
                </div>
            <div class="operational_settings">
                <h3>Rover Operations</h3>
                <div><input type="checkbox" value="rover_on"><p>Turn Rover On</p>
                <p>Checking this box turns the rover on or off.</p>
                </div>                
                <div><input type="checkbox" value="computer_vision"><p>Enable Computer Vision Processing</p>
                <p>Checking this box allows the simulator to process CV data as well as its other functions.</p></div>
            </div>
            <div class="download_upload" id="dl_up">
                <h3>Download/Upload Test Cases</h3>
                <p>Clicking the "Upload Test Case" button will allow you to select a properly formatted .json file to specify a test case</p>
                <button type="button">Upload Test Case</button>
                <p>Please specify a name for the test case you want to download in the textbox below, then hit "Download Test Case"</p>
                <input type="text" v-model="value">
                <button type="button">Download Test Case</button>
            </div>
        </div>
    </div>
    
    <script>
        var sim = new Vue({
            /*to make your life easy debugging this, install https://github.com/vuejs/vue-devtools in ya browser
            this section establishes all variables linked to some inputs/outputs on screen
            all variables used to update DOM !!MUST!! be registered in this data: object before use*/
            el: '#dl_up',
            data:{
                value: 'You liking the Vue, baby?'
            }
            import LCMBridge from 'lcm_bridge_client/dist/bridge.js'
            export default {
            name: 'Simulator',
            data () {
                return {
                lcm_: null,

                lastServosMessage: {
                    pan: 0,
                    tilt: 0
                },

                odom: {
                    latitude_deg: 38,
                    latitude_min: 24.38226,
                    longitude_deg: -110,
                    longitude_min: -47.51724,
                    bearing_deg: 0,
                    speed: 0
                },

                connections: {
                    websocket: false,
                    lcm: false,
                    motors: false,
                    cameras: [false, false, false, false, false, false]
                },

                nav_status: {
                    completed_wps: 0,
                    missed_wps: 0,
                    total_wps: 0
                }
                }
            },

            methods: {
                publish: function (channel, payload) {
                this.lcm_.publish(channel, payload)
                },

                subscribe: function (channel, callbackFn) {
                if( (typeof callbackFn !== "function") || (callbackFn.length !== 1)) {
                    console.error("Callback Function is invalid (should take 1 parameter)")
                }
                this.lcm_.subscribe(channel, callbackFn)
                }
            },

            created: function () {
                this.lcm_ = new LCMBridge(
                'ws://localhost:8020',
                // Update WebSocket connection state
                (online) => {
                    this.lcm_.setHomePage()
                    this.connections.websocket = online
                },
                // Update connection states
                (online) => {
                    this.connections.lcm = online[0],
                    this.connections.cameras = online.slice(1)
                },
                // Subscribed LCM message received
                (msg) => {
                    if (msg.topic === '/odometry') {
                    this.odom = msg.message
                    } else if (msg.topic === '/kill_switch') {
                    this.connections.motors = !msg.message.killed
                    } else if (msg.topic === '/debugMessage') {
                    if (msg['message']['isError']) {
                        console.error(msg['message']['message'])
                    } else {
                        console.log(msg['message']['message'])
                    }
                    }
                },
                // Subscriptions
                [
                    {'topic': '/odometry', 'type': 'Odometry'},
                    {'topic': '/sensors', 'type': 'Sensors'},
                    {'topic': '/temperature', 'type': 'Temperature'},
                    {'topic': '/kill_switch', 'type': 'KillSwitch'},
                    {'topic': '/camera_servos', 'type': 'CameraServos'},
                    {'topic': '/encoder', 'type': 'Encoder'},
                    {'topic': '/nav_status', 'type': 'NavStatus'},
                    {'topic': '/debugMessage', 'type': 'DebugMessage'}
                ]
                )

        })
    </script>
</body> 
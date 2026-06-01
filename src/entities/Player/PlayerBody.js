import * as THREE from 'three'
import Component from '../../Component'


// Full-body representation of the player (placeholder: the mutant humanoid rig).
// The first-person arms (Hands) stay on the camera for the local view; this body
// lives in the world at the player's capsule, plays locomotion animations driven by
// movement, and casts a shadow. By default it's rendered only on a dedicated layer
// the FP camera ignores (so you see its shadow, not a monster in your face) while the
// level's shadow light still sees that layer. Flip visibleToPlayer to show it in-view
// (useful once a real soldier mesh replaces the mutant) or for third-person.
const BODY_LAYER = 1;

export default class PlayerBody extends Component{
    constructor(model, clips, scene, camera){
        super();
        this.name = 'PlayerBody';
        this.model = model;
        this.clips = clips;
        this.scene = scene;
        this.camera = camera;

        this.animations = {};
        this.currentState = null;
        this.playerControls = null;
        this.rootBone = null;

        // Vertical offset from the capsule-tracked position (camera height) down to
        // the feet. Capsule is 1.9m tall and the camera sits 0.5 above its centre.
        this.feetOffset = -1.45;
        // Yaw correction so the mutant (faces +Z) aligns with the look direction.
        this.yawOffset = Math.PI;
        // Hidden from the FP camera by default; still casts a shadow.
        this.visibleToPlayer = false;
    }

    SetupAnimations(){
        this.mixer = new THREE.AnimationMixer(this.model);
        ['idle', 'walk', 'run'].forEach(name => {
            if(this.clips[name]){
                this.animations[name] = this.mixer.clipAction(this.clips[name]);
            }
        });
    }

    Initialize(){
        this.playerControls = this.GetComponent('PlayerControls');

        const model = this.model;
        model.scale.setScalar(0.01);

        model.traverse(child => {
            if(!child.isSkinnedMesh){
                return;
            }
            child.frustumCulled = false;
            child.castShadow = true;
            child.receiveShadow = true;
            if(!this.visibleToPlayer){
                child.layers.set(BODY_LAYER);
            }
            this.rootBone = child.skeleton.bones.find(b => b.name === 'MutantHips');
        });

        if(this.rootBone){
            this.rootRefPos = this.rootBone.position.clone();
        }

        this.SetupAnimations();
        this.scene.add(model);

        // Keep the body out of the FP camera but in the shadow pass: it renders only
        // on BODY_LAYER, so let the level's shadow-casting light see that layer too.
        if(!this.visibleToPlayer){
            let light = null;
            this.scene.traverse(o => { if(o.isLight && o.shadow){ light = o; } });
            if(light){
                light.shadow.camera.layers.enable(BODY_LAYER);
            }
        }

        this.SetState('idle');
    }

    SetState(name){
        if(this.currentState === name || !this.animations[name]){
            return;
        }

        const next = this.animations[name];
        next.reset();
        next.setEffectiveWeight(1.0);
        next.setEffectiveTimeScale(1.0);
        next.play();

        if(this.currentState && this.animations[this.currentState]){
            next.crossFadeFrom(this.animations[this.currentState], 0.2, true);
        }

        this.currentState = name;
    }

    Update(t){
        if(!this.mixer){
            return;
        }

        this.mixer.update(t);

        // In-place animation: lock the hips horizontally so the walk/run root motion
        // doesn't slide the body off the capsule (keep Y so it still bobs).
        if(this.rootBone){
            this.rootBone.position.x = this.rootRefPos.x;
            this.rootBone.position.z = this.rootRefPos.z;
        }

        // Follow the capsule and face the look direction.
        const p = this.parent.Position;
        this.model.position.set(p.x, p.y + this.feetOffset, p.z);
        this.model.rotation.set(0, this.playerControls.angles.y + this.yawOffset, 0);

        // Drive locomotion from movement state.
        const speed = this.playerControls.HorizontalSpeed;
        const grounded = this.playerControls.IsGrounded;
        let desired = 'idle';
        if(speed > 0.5 && grounded){
            desired = this.playerControls.isSprinting ? 'run' : 'walk';
        }
        this.SetState(desired);
    }
}

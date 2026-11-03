from pathlib import Path
import json, re

root=Path(__file__).resolve().parent
src=root/"src/main/java/com/mechanicaluniverse/MechanicalUniverse.java"
code=src.read_text(encoding="utf-8")
tiers=["wooden","iron","brass","steel","reinforced"]
groups={
"transmission":"gear,reducer,differential,clutch,sprocket,gearbox,flywheel,ratchet,cam,pulley",
"shaft":"shaft,bearing,coupling,joint,brake,chain,belt,connector,sleeve,axle",
"engine":"engine,turbine,generator,rotor,crankcase,piston,starter,cooler,igniter,fuel_injector",
"machine":"press,crusher,sawmill,lathe,drill,mill,mixer,separator,grinder,extruder",
"hydraulic":"pump,cylinder,manifold,valve,piston,accumulator,filter,regulator,hose,reservoir",
"pneumatic":"compressor,air_tank,nozzle,actuator,valve,dryer,air_filter,airlock,regulator,air_motor",
"electric":"motor,generator,transformer,battery,cable,breaker,capacitor,converter,resistor,relay",
"logistics":"conveyor,sorter,loader,unloader,splitter,hopper,feeder,ejector,collector,distributor",
"robotics":"arm,gripper,joint,servo,controller,positioner,turntable,sensor,toolhead,robot_base",
"vehicle":"wheel,axle,suspension,steering,transmission,brake,propeller,chassis,track,hub",
"construction":"winch,crane,hoist,lift,drill_rig,pile_driver,pulley,excavator_arm,jack,platform",
"chemistry":"reactor,distiller,centrifuge,mixer,filter,extractor,condenser,dryer,fermenter,separator",
"fluid":"pipe,tank,pump,flow_meter,valve,splitter,mixer,injector,heater,tap",
"control":"controller,sensor,timer,logic_gate,switch,counter,meter,panel,comparator,sequencer",
"structure":"frame,support,beam,plate,hinge,joint,rotator,bearing_block,platform,mount"
}
pieces=[t+"_"+family+"_"+name for t in tiers for family,items in groups.items() if not(t=="reinforced" and family=="structure") for name in items.split(",")]
original=re.search(r'static \{ for\(String name:new String\[\]\{(.*?)\}\) part\(name\);',code, re.S)
if not original:
 raise RuntimeError("Cannot find original prototype registration")
base=re.findall(r'"([^"]+)"',original.group(1))
assert len(base)==60 and len(pieces)==740 and len(set(base+pieces))==800
part_names=base+pieces

factory_registry="""
 static final RegistryObject<Block> EMERALD_FACTORY=BLOCKS.register("infinite_emerald_factory",()->new InfiniteFactory(Items.EMERALD));
 static final RegistryObject<Block> DIAMOND_FACTORY=BLOCKS.register("infinite_diamond_factory",()->new InfiniteFactory(Items.DIAMOND));
 static final RegistryObject<Item> EMERALD_ITEM=ITEMS.register("infinite_emerald_factory",()->new BlockItem(EMERALD_FACTORY.get(),new Item.Properties()));
 static final RegistryObject<Item> DIAMOND_ITEM=ITEMS.register("infinite_diamond_factory",()->new BlockItem(DIAMOND_FACTORY.get(),new Item.Properties()));
 """
code=code.replace(" static { for(String name:",factory_registry+"\n static { for(String name:",1)
# Inject extra blocks and the factory items right after the original 60 entries.
insert="".join(' part("'+s+'");' for s in pieces)
code=code.replace(" TAB_ITEMS.add(LAVA_ITEM);",insert+" TAB_ITEMS.add(EMERALD_ITEM);TAB_ITEMS.add(DIAMOND_ITEM);TAB_ITEMS.add(LAVA_ITEM);",1)
factory_class="""
 public static class InfiniteFactory extends Block {
  private final Item output;
  public InfiniteFactory(Item output){super(BlockBehaviour.Properties.copy(Blocks.IRON_BLOCK).strength(5f));this.output=output;}
  @Override public void onPlace(BlockState state,Level world,BlockPos pos,BlockState oldState,boolean moving){
   super.onPlace(state,world,pos,oldState,moving);
   if(!world.isClientSide)world.scheduleTick(pos,this,40);
  }
  @Override public void tick(BlockState state,net.minecraft.server.level.ServerLevel world,BlockPos pos,net.minecraft.util.RandomSource random){
   if(!world.hasNeighborSignal(pos)){
    for(net.minecraft.core.Direction dir:net.minecraft.core.Direction.values()){
     var neighbor=world.getBlockEntity(pos.relative(dir));
     if(neighbor instanceof net.minecraft.world.Container container){
      boolean added=false;
      for(int i=0;i<container.getContainerSize();i++){
       ItemStack item=container.getItem(i);
       ItemStack gift=new ItemStack(output);
       if(!container.canPlaceItem(i,gift))continue;
       if(item.isEmpty()){container.setItem(i,gift);container.setChanged();added=true;break;}
       if(ItemStack.isSameItemSameTags(item,gift)&&item.getCount()<Math.min(item.getMaxStackSize(),container.getMaxStackSize())){
        item.grow(1);container.setChanged();added=true;break;
       }
      }
      if(added)break;
     }
    }
   }
   world.scheduleTick(pos,this,40);
  }
  @Override public InteractionResult use(BlockState state,Level world,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit){
   if(!world.isClientSide && hand==InteractionHand.MAIN_HAND){
    ItemStack gift=new ItemStack(output,8);
    if(!player.getInventory().add(gift))player.drop(gift,false);
   }
   return InteractionResult.sidedSuccess(world.isClientSide);
  }
 }
 """
code=code.replace(" public static class InfiniteSource extends Block {",factory_class+"\n public static class InfiniteSource extends Block {",1)
src.write_text(code,encoding="utf-8")

res=root/"src/main/resources"
namespace="mechanicaluniverse"
assets=res/"assets"/namespace
data=res/"data"/namespace/"recipes"
data.mkdir(parents=True,exist_ok=True)
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
for name in part_names+["infinite_lava_generator","infinite_water_generator","infinite_emerald_factory","infinite_diamond_factory"]:
 write(assets/"blockstates"/(name+".json"),{"variants":{"":{"model":f"{namespace}:block/{name}"}}})
 write(assets/"models/block"/(name+".json"),{"parent":"minecraft:block/cube_all","textures":{"all":"minecraft:block/iron_block"}})
 write(assets/"models/item"/(name+".json"),{"parent":f"{namespace}:block/{name}"})
 material="minecraft:netherite_block" if name in ["infinite_emerald_factory","infinite_diamond_factory"] else "minecraft:iron_ingot"
 write(data/(name+".json"),{"type":"minecraft:crafting_shaped","pattern":["III","IRI","III"],"key":{"I":{"item":material},"R":{"item":"minecraft:redstone_block"}},"result":{"item":f"{namespace}:{name}","count":1}})
write(assets/"models/item/eight_bucket.json",{"parent":"minecraft:item/generated","textures":{"layer0":"minecraft:item/bucket"}})
for language in ("en_us","ru_ru"):
 names={f"block.{namespace}.{name}":name.replace("_"," ").title() for name in part_names+["infinite_lava_generator","infinite_water_generator","infinite_emerald_factory","infinite_diamond_factory"]}
 names[f"item.{namespace}.eight_bucket"]="Ведро на восемь порций" if language=="ru_ru" else "Eight Bucket"
 tab_translations={
  "en_us":{
   "main":"Mechanical Universe - Basic Parts",
   "rotation":"Mechanical Universe - Gears and Shafts",
   "engines":"Mechanical Universe - Engines and Machines",
   "fluids":"Mechanical Universe - Hydraulics and Pneumatics",
   "electronics":"Mechanical Universe - Power and Control",
   "automation":"Mechanical Universe - Automation and Robotics",
   "transport":"Mechanical Universe - Vehicles and Construction",
   "processing":"Mechanical Universe - Chemistry and Fluids",
   "structures":"Mechanical Universe - Structural Parts"},
  "ru_ru":{
   "main":"Mechanical Universe — Основные детали",
   "rotation":"Mechanical Universe — Передачи и валы",
   "engines":"Mechanical Universe — Двигатели и станки",
   "fluids":"Mechanical Universe — Гидравлика и пневматика",
   "electronics":"Mechanical Universe — Электрика и управление",
   "automation":"Mechanical Universe — Автоматизация",
   "transport":"Mechanical Universe — Техника и строительство",
   "processing":"Mechanical Universe — Химия и жидкости",
   "structures":"Mechanical Universe — Конструкции"}
 }
 names.update({f"itemGroup.{namespace}.{key}":val for key,val in tab_translations[language].items()})
 write(assets/"lang"/(language+".json"),names)
print(f"Generated {len(part_names)} construction blocks, 4 source/factory blocks, and resources")

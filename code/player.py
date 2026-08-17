from sprites import *

class Player(Sprite):
    def __init__(self, game: Game, pos: Vector2, texture: Texture) -> None:
        self.game = game
        super().__init__(pos, texture)
        self.direction = Vector2()
        self.speed = PLAYER_SPEED
        self.hitbox_offset = PLAYER_HITBOX_OFFSET
        self.hitbox = Rectangle(self.pos.x, self.pos.y+self.hitbox_offset, self.texture.width, self.texture.height-self.hitbox_offset)

    @property
    def center(self) -> Vector2:
        return Vector2(self.pos.x + self.texture.width/2, self.pos.y + self.texture.height/2)   

    def update(self, dt: float) -> None:
        self.get_input()
        self.move(dt)

    def get_input(self) -> None:
        self.direction.x = int(is_action_down('move_right')) - int(is_action_down('move_left'))
        self.direction.y = int(is_action_down('move_down')) - int(is_action_down('move_up'))

        # stick
        if is_gamepad_available(0):
            stick_x = check_dead_zone(get_gamepad_axis_movement(0, GAMEPAD_AXIS_LEFT_X))
            stick_y = check_dead_zone(get_gamepad_axis_movement(0, GAMEPAD_AXIS_LEFT_Y))
            # check for controller movement
            if any((stick_x,stick_y)):
                self.direction.x = stick_x
                self.direction.y = stick_y

        # normalize
        if vector2_length(self.direction) > 1:
            self.direction = vector2_normalize(self.direction)

    def collisions(self, direction: str) -> None:
        if direction == 'horizontal':
            for collision_box in self.game.level.collision_boxes:
                if check_collision_recs(self.hitbox, collision_box):
                    if self.direction.x > 0:
                        self.hitbox.x = collision_box.x - self.hitbox.width 
                    elif self.direction.x < 0:
                        self.hitbox.x = collision_box.x + collision_box.width
        if direction == 'vertical':
            for collision_box in self.game.level.collision_boxes:
                if check_collision_recs(self.hitbox, collision_box):
                    if self.direction.y > 0:
                        self.hitbox.y = collision_box.y - self.hitbox.height
                    elif self.direction.y < 0:
                        self.hitbox.y = collision_box.y + collision_box.height
                    
    def move(self, dt: float) -> None:
        self.hitbox.x += self.direction.x * self.speed * dt
        self.collisions('horizontal')
        self.hitbox.y += self.direction.y * self.speed * dt
        self.collisions('vertical')
        self.pos = Vector2(self.hitbox.x, self.hitbox.y-self.hitbox_offset/2)
